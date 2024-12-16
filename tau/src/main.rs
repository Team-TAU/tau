use axum::extract::ws::{Message, WebSocket};
use axum::extract::{State, WebSocketUpgrade};
use axum::http::StatusCode;
use axum::response::Response;
use eventsub_ws::EventSubWebSocket;
use futures_util::SinkExt;
use futures_util::StreamExt;
use log::{debug, error, info, trace, warn};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sqlx::postgres::PgPoolOptions;
use sqlx::{Pool, Postgres};
use std::collections::{HashMap, HashSet};
use std::net::Ipv4Addr;
use std::sync::Arc;
use tokio::sync::{broadcast, Mutex};
use twitch_oauth2::{CsrfToken, UserTokenBuilder};
use utoipa::openapi::security::{HttpAuthScheme, HttpBuilder, SecurityScheme};
use utoipa::openapi::Components;

use tokio::net::TcpListener;
use utoipa::{Modify, OpenApi, ToSchema};
use utoipa_axum::router::OpenApiRouter;
use utoipa_axum::routes;
use utoipa_swagger_ui::SwaggerUi;

mod eventsub_ws;
mod kv_store;
mod settings;

const AUTH_TAG: &str = "auth";
const TWITCH_TAG: &str = "twitch";

use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("uh oh")]
    Anyhow(#[from] anyhow::Error),
    #[error("unauthorized")]
    Unauthorized,
    #[error("csrf error")]
    CsrfError,
}

impl axum::response::IntoResponse for AppError {
    fn into_response(self) -> axum::response::Response {
        let status = match &self {
            AppError::Anyhow(err) => {
                error!("{}", err);
                StatusCode::INTERNAL_SERVER_ERROR
            }
            AppError::Unauthorized => StatusCode::UNAUTHORIZED,
            AppError::CsrfError => StatusCode::UNAUTHORIZED,
        };
        (status, self.to_string()).into_response()
    }
}

#[derive(OpenApi)]
#[openapi(
    tags(
        (name = AUTH_TAG, description = "Auth API endpoints"),
        (name = TWITCH_TAG, description = "Twitch API endpoints"),
    ),
        modifiers(&SecurityAddon)
)]
struct ApiDoc;

struct SecurityAddon;

impl Modify for SecurityAddon {
    fn modify(&self, openapi: &mut utoipa::openapi::OpenApi) {
        if openapi.components.is_none() {
            openapi.components = Some(Components::new());
        }

        openapi.components.as_mut().unwrap().add_security_scheme(
            "bearerAuth",
            SecurityScheme::Http(
                HttpBuilder::new()
                    .scheme(HttpAuthScheme::Bearer)
                    .bearer_format("JWT")
                    .build(),
            ),
        );
    }
}

/// Get health of the API.
#[utoipa::path(method(get), path = "/ws/twitch-events/")]
async fn ws_events(ws: WebSocketUpgrade, State(state): State<Arc<crate::RouterState>>) -> Response {
    ws.on_upgrade(|socket| handle_socket(socket, state))
}

async fn handle_socket(stream: WebSocket, state: Arc<crate::RouterState>) {
    // TODO: require authentication
    let (mut sender, mut receiver) = stream.split();
    while let Some(Ok(msg)) = receiver.next().await {
        println!("{}", msg.to_text().unwrap());
        break;
    }
    let mut rx = state.broadcast_event.subscribe();

    let mut send_task = tokio::spawn(async move {
        while let Ok(msg) = rx.recv().await {
            // In any websocket error, break loop.
            let msg = serde_json::to_string(&msg).unwrap();
            if sender.send(Message::Text(msg)).await.is_err() {
                println!("ahhhhh");
                break;
            }
        }
    });

    // let msg = "hi".to_string();
    // let _ = state.broadcast_event.send(msg);

    let mut recv_task = tokio::spawn(async move {
        while let Some(Ok(Message::Text(text))) = receiver.next().await {
            // Add username before message.
            println!("{}", text);
        }
    });

    tokio::select! {
        _ = &mut send_task => recv_task.abort(),
        _ = &mut recv_task => send_task.abort(),
    };
}

/// Get health of the API.
#[utoipa::path(
    method(get, head),
    path = "/api/v1/health",
    responses(
        (status = OK, description = "Success", body = str, content_type = "text/plain")
    ),
    security(
      ("bearerAuth" = [])
    ),
)]
async fn health() -> &'static str {
    "ok"
}

pub struct TwitchApiSpec {
    pub event_sub: Vec<EventSub>,
    pub helix: Vec<HelixEndpoint>,
    pub scopes: HashSet<String>,
}
pub struct RouterState {
    pub pool: Pool<Postgres>,
    pub oauth_state: Mutex<HashMap<CsrfToken, UserTokenBuilder>>,
    pub kv: kv_store::KVStore,
    pub config: settings::Settings,
    pub broadcast_event: broadcast::Sender<crate::events::Event>,
    pub spec: TwitchApiSpec,
}

#[derive(ToSchema, Serialize, Deserialize, Clone)]
pub struct ConditionSchema {
    pub required: Vec<String>,
}

#[derive(ToSchema, Serialize, Deserialize, Clone)]
pub struct EventSub {
    pub subscription_type: String,
    pub name: String,
    pub version: String,
    pub description: String,
    pub scope_required: Option<String>,
    pub event_schema: Value,
    pub condition_schema: ConditionSchema,
}

#[derive(ToSchema, Serialize, Deserialize, Clone, Debug, PartialEq, Eq)]
pub enum TokenType {
    #[serde(rename = "OAuth")]
    UserToken,
    #[serde(rename = "AppAccess")]
    AppAccessToken,
}

#[derive(ToSchema, Serialize, Deserialize, Clone)]
pub struct HelixEndpoint {
    pub description: String,
    pub endpoint: String,
    pub method: String,
    pub reference_url: String,
    pub token_type: TokenType,
    pub scope: Option<String>,
}

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    colog::init();
    let eventsub_spec: Vec<EventSub> =
        serde_json::from_str(include_str!("../../eventsub_subscriptions.json")).unwrap();
    let helix_spec: Vec<HelixEndpoint> =
        serde_json::from_str(include_str!("../../helix_endpoints.json")).unwrap();
    let scopes: std::collections::HashSet<String> = eventsub_spec
        .iter()
        .filter_map(|spec| spec.scope_required.clone())
        .chain(helix_spec.iter().filter_map(|spec| spec.scope.clone()))
        .collect();

    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect("postgres://root:root@localhost/tau_db")
        .await?;

    let mut kv = kv_store::KVStore::new();

    let (tx, _rx) = broadcast::channel::<crate::events::Event>(100);

    dotenvy::dotenv()?;

    // TODO: check if '_sqlx_migrations' table exists;
    // if not, run a pgdump to a backup file
    let initial_migration = false;
    if initial_migration {
        kv.migrate(&pool).await?;
    } else {
        let result = kv.load(&pool).await;
        match result {
            Err(e) => {
                // This is not fatal - this is the expected flow
                // for a fresh install
                println!("Failed to load KV store.\nFalling back to defaults.\n{}", e);
            }
            _ => {}
        }
    }
    sqlx::migrate!().run(&pool).await?;
    kv.save(&pool).await?;

    // import new EventSub subscriptions
    for sub in eventsub_spec.iter() {
        sqlx::query!(
            "INSERT INTO twitch_twitcheventsubsubscription
        (name, version, active) VALUES ($1, $2, $3)
        ON CONFLICT (name) DO UPDATE SET active = ((SELECT version FROM twitch_twitcheventsubsubscription WHERE name = EXCLUDED.name) = EXCLUDED.version), version = EXCLUDED.VERSION",
            &sub.name,
            &sub.version,
            false
        )
        .execute(&pool)
        .await
        .unwrap();
    }

    let state = Arc::new(RouterState {
        broadcast_event: tx,
        pool,
        oauth_state: HashMap::new().into(),
        config: settings::Settings {
            twitch_app_id: std::env::var("TWITCH_APP_ID").unwrap(),
            twitch_client_secret: std::env::var("TWITCH_CLIENT_SECRET").unwrap(),
            superuser: "badcop_".to_string(),
        },
        spec: TwitchApiSpec {
            event_sub: eventsub_spec,
            helix: helix_spec,
            scopes,
        },
        kv: kv.into(),
    });
    let (router, api) = OpenApiRouter::with_openapi(ApiDoc::openapi())
        .routes(routes!(health))
        .routes(routes!(ws_events))
        .nest("/api/v1/auth", auth::router())
        .nest("/api/v1/twitch-events", events::router())
        .nest("/api/v1/streamers", streamers::router())
        .routes(routes!(twitch::get_helix_endpoints))
        .routes(routes!(twitch::helix_passthrough))
        .with_state(state.clone())
        .split_for_parts();

    let router = router.merge(SwaggerUi::new("/swagger-ui").url("/apidoc/openapi.json", api));

    let state = state.clone();
    // TODO: uncomment
    // tokio::spawn(async {
    //     let websocket = EventSubWebSocket::new(state);
    //     websocket.run_loop().await;
    // });

    let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 3000)).await?;
    axum::serve(listener, router).await?;
    Ok(())
}

mod twitch {
    use std::sync::Arc;

    use anyhow::Context as _;
    use axum::extract::{Json, Path, State};
    use axum::http::StatusCode;
    use axum::response::{IntoResponse, Redirect};
    use log::{debug, error, info, trace, warn};
    use reqwest::{Method, Url};
    use serde::{Deserialize, Serialize};
    use twitch_api::twitch_oauth2::UserTokenBuilder;
    use twitch_oauth2::CsrfToken;
    use utoipa_axum::router::OpenApiRouter;
    use utoipa_axum::routes;

    #[utoipa::path(get, path = "/api/v1/twitch/helix-endpoints",
        responses(
        (status = OK, body = Vec<crate::HelixEndpoint>),
    ), tag = super::TWITCH_TAG)]
    pub async fn get_helix_endpoints(
        State(state): State<Arc<crate::RouterState>>,
    ) -> Result<impl IntoResponse, crate::AppError> {
        Ok(Json(state.spec.helix.clone()))
    }

    #[utoipa::path(method(get, post, patch, put, delete), path = "/api/twitch/helix/:path",
        responses(
        (status = OK, body = Vec<crate::HelixEndpoint>),
    ), tag = super::TWITCH_TAG)]
    pub async fn helix_passthrough(
        State(state): State<Arc<crate::RouterState>>,
        Path(path): Path<String>,
        method: Method,
    ) -> Result<impl IntoResponse, crate::AppError> {
        // TODO: require authentication
        let access_token = state
            .kv
            .refresh_access_token(&state.config, &state.pool)
            .await?;
        let client = reqwest::Client::new();
        let dest = format!("https://api.twitch.tv/helix/{}", path);
        info!("{}: {}", method, dest);
        let response = client
            .request(method, dest)
            .header("Authorization", format!("Bearer {}", access_token.secret()))
            .header("Client-Id", &state.config.twitch_app_id)
            .send()
            .await
            .context("spaghetti")?;
        let status = response.status().clone();
        let json: sqlx::types::JsonValue = response.json().await.context("not json")?;
        Ok((status, Json(json)).into_response())
    }
}

mod auth {
    use std::sync::Arc;

    use anyhow::Context as _;
    use axum::extract::{Json, State};
    use axum::http::StatusCode;
    use axum::response::{IntoResponse, Redirect};
    use reqwest::Url;
    use serde::{Deserialize, Serialize};
    use twitch_api::twitch_oauth2::UserTokenBuilder;
    use twitch_oauth2::CsrfToken;
    use utoipa::ToSchema;
    use utoipa_axum::router::OpenApiRouter;
    use utoipa_axum::routes;

    #[derive(ToSchema, Serialize)]
    struct LoginResponse {
        token: String,
        username: String,
    }

    #[derive(ToSchema, Serialize)]
    struct ScopeResponse {
        scope: String,
        required: bool,
    }

    #[derive(ToSchema, Serialize, Deserialize)]
    struct TokenRequest {
        username: String,
        password: String,
    }

    #[derive(ToSchema, Serialize, Deserialize)]
    struct OauthRequest {
        state: String,
        code: String,
    }

    pub fn router() -> OpenApiRouter<Arc<crate::RouterState>> {
        OpenApiRouter::new()
            .routes(routes!(post_token_auth))
            .routes(routes!(login_auth))
            .routes(routes!(login_redirect_landing))
            .routes(routes!(get_scopes))
    }

    #[utoipa::path(get, path = "/login",
        responses(
        (status = FOUND, body = ()),
    ), tag = super::AUTH_TAG)]
    async fn login_auth(
        State(state): State<Arc<crate::RouterState>>,
    ) -> Result<impl IntoResponse, crate::AppError> {
        let mut builder = UserTokenBuilder::new(
            state.config.twitch_app_id.as_str(),
            state.config.twitch_client_secret.as_str(),
            Url::parse("http://localhost:5173/twitch-callback/")
                .context("failed to parse redirect URL")?,
        );
        let (url, csrf_token) = builder.generate_url();

        let mut cache = state.oauth_state.lock().await;
        cache.insert(csrf_token, builder);
        drop(cache);

        Ok(Redirect::temporary(url.as_str()))
    }

    #[utoipa::path(post, path = "/oauth",
        responses(
        (status = FOUND),
        (status = UNAUTHORIZED),
    ), tag = super::AUTH_TAG)]
    async fn login_redirect_landing(
        State(state): State<Arc<crate::RouterState>>,
        Json(payload): Json<OauthRequest>,
    ) -> Result<impl IntoResponse, crate::AppError> {
        let mut cache = state.oauth_state.lock().await;
        let builder = cache
            .remove(&CsrfToken::from(payload.state.as_str()))
            .ok_or(crate::AppError::CsrfError)?;
        drop(cache);
        let client = reqwest::Client::builder()
            .redirect(reqwest::redirect::Policy::none())
            .build()
            .context("failed to create reqwest client")?;
        let token = builder
            .get_user_token(&client, payload.state.as_ref(), payload.code.as_ref())
            .await
            .context("failed to get user token")?;
        let twitch_client = twitch_api::HelixClient::with_client(client);
        let user_info = twitch_client
            .get_user_from_id(&token.user_id, &token)
            .await
            .context("failed to get user info")?
            .ok_or(crate::AppError::Unauthorized)?;
        if user_info.login.to_string() == state.config.superuser {
            Ok((
                StatusCode::OK,
                Json(LoginResponse {
                    token: "special_token".to_string(),
                    username: user_info.login.to_string(),
                }),
            ))
        } else {
            Err(crate::AppError::Unauthorized)
        }
    }

    #[utoipa::path(get, path = "/scopes",
        responses(
        (status = OK, body = Vec<ScopeResponse>),
        (status = FORBIDDEN, body = ())
    ), tag = super::AUTH_TAG)]
    #[axum::debug_handler]
    async fn get_scopes(
        State(state): State<Arc<crate::RouterState>>,
    ) -> Result<impl IntoResponse, crate::AppError> {
        // TODO: require authentication
        let access_token = state
            .kv
            .refresh_access_token(&state.config, &state.pool)
            .await?;
        let client = reqwest::Client::new();
        let req = client
            .get(twitch_oauth2::VALIDATE_URL.as_str())
            .header("Authorization", format!("Bearer {}", access_token.secret()))
            .header("Content-Type", "application/json")
            .send()
            .await
            .context("failed to validate")?;

        let resp: twitch_oauth2::ValidatedToken = req.json().await.context("failed to validate")?;
        let scopes = resp.scopes.ok_or(anyhow::anyhow!("no scopes wut"))?;

        let response: Vec<_> = state
            .spec
            .scopes
            .iter()
            .map(|scope| ScopeResponse {
                scope: scope.clone(),
                required: scopes
                    .iter()
                    .find(|active| active.as_str() == scope)
                    .is_some(),
            })
            .collect();

        // let row = sqlx::query!(
        //     "SELECT id FROM users_user WHERE username = $1",
        //     payload.username
        // )
        // .fetch_optional(&state.pool)
        // .await
        // .context("")?;
        // if let Some(_) = row {
        //     if payload.password == "hunter2" {
        //         Ok((
        //             StatusCode::OK,
        //             Json(LoginResponse {
        //                 token: String::from("*******"),
        //                 username: "".to_string(),
        //             }),
        //         )
        //             .into_response())
        //     } else {
        //         Ok(StatusCode::FORBIDDEN.into_response())
        //     }
        // } else {
        //     Ok(StatusCode::FORBIDDEN.into_response())
        // }
        Ok(Json(response))
    }

    #[utoipa::path(post, path = "/token",
        responses(
        (status = OK, body = LoginResponse),
        (status = FORBIDDEN, body = ())
    ), tag = super::AUTH_TAG)]
    #[axum::debug_handler]
    async fn post_token_auth(
        State(state): State<Arc<crate::RouterState>>,
        Json(payload): Json<TokenRequest>,
    ) -> Result<impl IntoResponse, crate::AppError> {
        // TODO: require authentication
        state
            .kv
            .refresh_access_token(&state.config, &state.pool)
            .await;
        // let row = sqlx::query!(
        //     "SELECT id FROM users_user WHERE username = $1",
        //     payload.username
        // )
        // .fetch_optional(&state.pool)
        // .await
        // .context("")?;
        // if let Some(_) = row {
        //     if payload.password == "hunter2" {
        //         Ok((
        //             StatusCode::OK,
        //             Json(LoginResponse {
        //                 token: String::from("*******"),
        //                 username: "".to_string(),
        //             }),
        //         )
        //             .into_response())
        //     } else {
        //         Ok(StatusCode::FORBIDDEN.into_response())
        //     }
        // } else {
        //     Ok(StatusCode::FORBIDDEN.into_response())
        // }
        Ok(())
    }
}
mod streamers {
    use std::sync::Arc;

    use anyhow::Context as _;
    use axum::extract::State;
    use axum::extract::{Json, Path};
    use axum::response::IntoResponse;
    use chrono::{DateTime, Utc};
    use serde::{Deserialize, Serialize};
    use utoipa::ToSchema;
    use utoipa_axum::router::OpenApiRouter;
    use utoipa_axum::routes;
    use uuid::Uuid;

    pub fn router() -> OpenApiRouter<Arc<crate::RouterState>> {
        OpenApiRouter::new()
            .routes(routes!(get_streamers))
            .routes(routes!(delete_streamer))
            .routes(routes!(add_streamer))
    }

    #[derive(ToSchema, Serialize, Deserialize, Clone, Debug)]
    struct Streamer {
        id: Uuid,
        twitch_username: String,
        twitch_id: Option<String>,
        streaming: bool,
        disabled: bool,
        created: DateTime<Utc>,
        updated: DateTime<Utc>,
    }

    #[derive(ToSchema, Serialize, Deserialize, Clone, Debug)]
    struct StreamersResponse {
        results: Vec<Streamer>,
    }

    #[utoipa::path(get, path = "", responses((status = OK, body = StreamersResponse)))]
    async fn get_streamers(
        State(state): State<Arc<crate::RouterState>>,
    ) -> Result<impl IntoResponse, crate::AppError> {
        // TODO: require authentication
        let rows = sqlx::query_as!(
            Streamer,
            "SELECT
                id,
                twitch_username,
                twitch_id,
                streaming,
                disabled,
                created,
                updated
            FROM streamers_streamer"
        )
        .fetch_all(&state.pool)
        .await
        .context("")?;

        let response = StreamersResponse { results: rows };
        Ok(Json(response))
    }

    #[derive(ToSchema, Serialize, Deserialize, Clone, Debug)]
    struct AddStreamerRequest {
        twitch_username: String,
        disabled: bool,
    }

    #[utoipa::path(post, path = "", responses((status = OK)))]
    async fn add_streamer(
        State(state): State<Arc<crate::RouterState>>,
        Json(payload): Json<AddStreamerRequest>,
    ) -> Result<impl IntoResponse, crate::AppError> {
        // TODO: require authentication
        let now = chrono::offset::Utc::now();
        let id: Option<String> = None;
        let result = sqlx::query_as!(
            Streamer,
            "INSERT INTO streamers_streamer
            (id, twitch_username, twitch_id, streaming, disabled, created, updated)
     VALUES ($1, $2, $3, False, $4, $5, $6)
           RETURNING
                id,
                twitch_username,
                twitch_id,
                streaming,
                disabled,
                created,
                updated",
            Uuid::new_v4(),
            payload.twitch_username,
            id,
            payload.disabled,
            &now,
            &now
        )
        .fetch_one(&state.pool)
        .await
        .context("")?;

        Ok(Json(result))
    }
    #[utoipa::path(delete, path = "/:uuid", responses((status = OK)))]
    async fn delete_streamer(
        State(state): State<Arc<crate::RouterState>>,
        Path(user_id): Path<Uuid>,
    ) -> Result<impl IntoResponse, crate::AppError> {
        // TODO: require authentication
        sqlx::query!("DELETE FROM streamers_streamer WHERE id = $1", user_id)
            .execute(&state.pool)
            .await
            .context("")?;

        Ok(())
    }
}

mod events {
    use std::sync::Arc;

    use anyhow::Context as _;
    use axum::extract::State;
    use axum::response::IntoResponse;
    use axum::Json;
    use chrono::{DateTime, Utc};
    use serde::{Deserialize, Serialize};
    use sqlx::types::Uuid;
    use utoipa::ToSchema;
    use utoipa_axum::router::OpenApiRouter;
    use utoipa_axum::routes;

    /// expose the Customer OpenAPI to parent module
    pub fn router() -> OpenApiRouter<Arc<crate::RouterState>> {
        OpenApiRouter::new().routes(routes!(get_events))
    }

    #[derive(ToSchema, Serialize, Deserialize, Clone, Debug)]
    pub struct Event {
        pub id: Uuid,
        pub event_id: Option<String>,
        pub event_data: sqlx::types::JsonValue,
        pub event_type: String,
        pub event_source: String,
        pub created: DateTime<Utc>,
        pub origin: Option<String>,
    }
    type Events = Vec<Event>;

    #[derive(ToSchema, Serialize, Deserialize)]
    struct Paginated<T> {
        next: Option<String>,
        previous: Option<String>,
        results: T,
    }
    #[utoipa::path(get, path = "", responses((status = OK, body = Paginated<Events>)))]
    async fn get_events(
        State(state): State<Arc<crate::RouterState>>,
    ) -> Result<impl IntoResponse, crate::AppError> {
        // TODO: require authentication
        let mut rows = sqlx::query_as!(
            Event,
            "SELECT
                id,
                event_id,
                event_data,
                event_type,
                event_source,
                created,
                NULL as origin
            FROM twitchevents_twitchevent
            ORDER BY created DESC
            LIMIT 10"
        )
        .fetch_all(&state.pool)
        .await
        .context("")?;

        for row in rows.iter_mut() {
            row.origin = Some("twitch".to_string());
        }

        let response: Paginated<Events> = Paginated::<_> {
            results: rows,
            next: None,
            previous: None,
        };
        Ok(Json(response))
    }
}
