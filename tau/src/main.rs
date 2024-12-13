use axum::extract::ws::{Message, WebSocket};
use axum::extract::{State, WebSocketUpgrade};
use axum::http::StatusCode;
use axum::response::Response;
use eventsub_ws::EventSubWebSocket;
use futures_util::SinkExt;
use futures_util::StreamExt;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sqlx::postgres::PgPoolOptions;
use sqlx::{Pool, Postgres};
use std::collections::HashMap;
use std::net::Ipv4Addr;
use std::sync::Arc;
use tokio::sync::{broadcast, Mutex};
use twitch_oauth2::{CsrfToken, UserTokenBuilder};
use utoipa::openapi::security::{HttpAuthScheme, HttpBuilder, SecurityScheme};
use utoipa::openapi::Components;

use tokio::net::TcpListener;
use utoipa::{Modify, OpenApi};
use utoipa_axum::router::OpenApiRouter;
use utoipa_axum::routes;
use utoipa_swagger_ui::SwaggerUi;

mod eventsub_ws;
mod kv_store;
mod settings;

const AUTH_TAG: &str = "auth";

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
        let status = match self {
            AppError::Anyhow(..) => StatusCode::INTERNAL_SERVER_ERROR,
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
    let (mut sender, mut receiver) = stream.split();
    while let Some(Ok(msg)) = receiver.next().await {
        println!("{}", msg.to_text().unwrap());
        break;
    }
    let mut rx = state.broadcast_event.subscribe();

    let mut send_task = tokio::spawn(async move {
        while let Ok(msg) = rx.recv().await {
            // In any websocket error, break loop.
            println!("Sending {}", msg);
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
    path = "/api/health",
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

pub struct RouterState {
    pub pool: Pool<Postgres>,
    pub oauth_state: Mutex<HashMap<CsrfToken, UserTokenBuilder>>,
    pub kv: kv_store::KVStore,
    pub config: settings::Settings,
    pub broadcast_event: broadcast::Sender<String>,
}

#[derive(Serialize, Deserialize)]
struct EventSub {
    subscription_type: String,
    name: String,
    version: String,
    description: String,
    scope_required: Option<String>,
    event_schema: Value,
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq)]
pub enum TokenType {
    #[serde(rename = "OAuth")]
    UserToken,
    #[serde(rename = "AppAccess")]
    AppAccessToken,
}

#[derive(Serialize, Deserialize)]
struct HelixEndpoint {
    description: String,
    endpoint: String,
    method: String,
    reference_url: String,
    token_type: TokenType,
    scope: Option<String>,
}

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    let eventsub_spec: Vec<EventSub> =
        serde_json::from_str(include_str!("../../eventsub_subscriptions.json")).unwrap();
    let helix_spec: Vec<HelixEndpoint> =
        serde_json::from_str(include_str!("../../helix_endpoints.json")).unwrap();
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect("postgres://root:root@localhost/tau_db")
        .await?;

    let mut kv = kv_store::KVStore::new();

    let (tx, _rx) = broadcast::channel::<String>(100);

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

    let state = Arc::new(RouterState {
        broadcast_event: tx,
        pool,
        oauth_state: HashMap::new().into(),
        config: settings::Settings {
            twitch_app_id: std::env::var("TWITCH_APP_ID").unwrap(),
            twitch_client_secret: std::env::var("TWITCH_CLIENT_SECRET").unwrap(),
            superuser: "badcop_".to_string(),
        },
        kv: kv.into(),
    });
    let (router, api) = OpenApiRouter::with_openapi(ApiDoc::openapi())
        .routes(routes!(health))
        .routes(routes!(ws_events))
        .nest("/api/v1/auth", auth::router())
        .nest("/api/v1/twitch-events", events::router())
        .routes(routes!(
            inner::secret_handlers::get_secret,
            inner::secret_handlers::post_secret
        ))
        .with_state(state.clone())
        .split_for_parts();

    let router = router.merge(SwaggerUi::new("/swagger-ui").url("/apidoc/openapi.json", api));

    let state = state.clone();
    tokio::spawn(async {
        let websocket = EventSubWebSocket::new(state);
        websocket.run_loop().await;
    });

    let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 3000)).await?;
    axum::serve(listener, router).await?;
    Ok(())
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
mod events {
    use std::sync::Arc;

    use anyhow::Context as _;
    use axum::extract::State;
    use axum::response::IntoResponse;
    use axum::Json;
    use chrono::{DateTime, Utc};
    use serde::{Deserialize, Serialize};
    use utoipa::ToSchema;
    use utoipa_axum::router::OpenApiRouter;
    use utoipa_axum::routes;

    /// expose the Customer OpenAPI to parent module
    pub fn router() -> OpenApiRouter<Arc<crate::RouterState>> {
        OpenApiRouter::new().routes(routes!(get_events))
    }

    #[derive(ToSchema, Serialize, Deserialize)]
    struct Event {
        id: String,
        event_id: Option<String>,
        event_data: sqlx::types::JsonValue,
        event_type: String,
        event_source: String,
        created: DateTime<Utc>,
        origin: Option<String>,
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
        let mut rows = sqlx::query_as!(Event, "SELECT id, event_id, event_data, event_type, event_source, created, NULL as origin FROM twitchevents_twitchevent LIMIT 10")
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

mod inner {
    pub mod secret_handlers {
        /// This is some secret inner handler
        #[utoipa::path(get, path = "/api/inner/secret", responses((status = OK, body = str)))]
        pub async fn get_secret() -> &'static str {
            "secret"
        }

        /// Post some secret inner handler
        #[utoipa::path(post, path = "/api/inner/secret", responses((status = OK)))]
        pub async fn post_secret() {
            println!("You posted a secret")
        }
    }
}
