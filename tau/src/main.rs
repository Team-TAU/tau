use axum::http::StatusCode;
use sqlx::postgres::PgPoolOptions;
use sqlx::{Pool, Postgres};
use std::net::Ipv4Addr;

use tokio::net::TcpListener;
use utoipa::OpenApi;
use utoipa_axum::router::OpenApiRouter;
use utoipa_axum::routes;
use utoipa_swagger_ui::SwaggerUi;

const CUSTOMER_TAG: &str = "customer";
const AUTH_TAG: &str = "auth";
const ORDER_TAG: &str = "order";

use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("uh oh")]
    Anyhow(#[from] anyhow::Error),
}

impl axum::response::IntoResponse for AppError {
    fn into_response(self) -> axum::response::Response {
        let status = match self {
            AppError::Anyhow(..) => StatusCode::INTERNAL_SERVER_ERROR,
        };
        (status, self.to_string()).into_response()
    }
}

#[derive(OpenApi)]
#[openapi(
    tags(
        (name = CUSTOMER_TAG, description = "Customer API endpoints"),
        (name = AUTH_TAG, description = "Auth API endpoints"),
        (name = ORDER_TAG, description = "Order API endpoints")
    )
)]
struct ApiDoc;

/// Get health of the API.
#[utoipa::path(
    method(get, head),
    path = "/api/health",
    responses(
        (status = OK, description = "Success", body = str, content_type = "text/plain")
    )
)]
async fn health() -> &'static str {
    "ok"
}

#[derive(Clone)]
pub struct RouterState {
    pub pool: Pool<Postgres>,
}

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect("postgres://root:root@localhost/tau_db")
        .await?;

    let state = RouterState { pool };

    let (router, api) = OpenApiRouter::with_openapi(ApiDoc::openapi())
        .routes(routes!(health))
        .nest("/api/v1/auth", auth::router())
        .nest("/api/v1/customer", customer::router())
        // .nest("/api/v1/order", order::router())
        .routes(routes!(
            inner::secret_handlers::get_secret,
            inner::secret_handlers::post_secret
        ))
        .with_state(state)
        .split_for_parts();

    let router = router.merge(SwaggerUi::new("/swagger-ui").url("/apidoc/openapi.json", api));

    let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 3000)).await?;
    axum::serve(listener, router).await?;
    Ok(())
}

mod auth {
    use anyhow::Context as _;
    use axum::extract::{Json, State};
    use axum::http::StatusCode;
    use axum::response::IntoResponse;
    use serde::{Deserialize, Serialize};
    use utoipa::ToSchema;
    use utoipa_axum::router::OpenApiRouter;
    use utoipa_axum::routes;

    #[derive(ToSchema, Serialize)]
    struct TokenResponse {
        token: String,
    }

    #[derive(ToSchema, Serialize, Deserialize)]
    struct TokenRequest {
        username: String,
        password: String,
    }

    pub fn router() -> OpenApiRouter<crate::RouterState> {
        OpenApiRouter::new().routes(routes!(post_token_auth))
    }

    #[utoipa::path(post, path = "/token",
        responses(
        (status = OK, body = TokenResponse),
        (status = FORBIDDEN, body = ()),
        (status = 500, body = ())
    ), tag = super::AUTH_TAG)]
    async fn post_token_auth(
        State(state): State<crate::RouterState>,
        Json(payload): Json<TokenRequest>,
    ) -> Result<impl IntoResponse, crate::AppError> {
        let row = sqlx::query!(
            "SELECT id FROM users_user WHERE username = $1",
            payload.username
        )
        .fetch_optional(&state.pool)
        .await
        .context("")?;
        if let Some(_) = row {
            if payload.password == "hunter2" {
                Ok((
                    StatusCode::OK,
                    Json(TokenResponse {
                        token: String::from("*******"),
                    }),
                )
                    .into_response())
            } else {
                Ok(StatusCode::FORBIDDEN.into_response())
            }
        } else {
            Ok(StatusCode::FORBIDDEN.into_response())
        }
    }
}
mod customer {
    use axum::Json;
    use serde::Serialize;
    use utoipa::ToSchema;
    use utoipa_axum::router::OpenApiRouter;
    use utoipa_axum::routes;

    /// This is the customer
    #[derive(ToSchema, Serialize)]
    struct Customer {
        name: String,
    }

    /// expose the Customer OpenAPI to parent module
    pub fn router() -> OpenApiRouter<crate::RouterState> {
        OpenApiRouter::new().routes(routes!(get_customer))
    }

    /// Get customer
    ///
    /// Just return a static Customer object
    #[utoipa::path(get, path = "", responses((status = OK, body = Customer)), tag = super::CUSTOMER_TAG)]
    async fn get_customer() -> Json<Customer> {
        Json(Customer {
            name: String::from("Bill Book"),
        })
    }
}

mod order {
    use axum::Json;
    use serde::{Deserialize, Serialize};
    use utoipa::ToSchema;
    use utoipa_axum::router::OpenApiRouter;
    use utoipa_axum::routes;

    /// This is the order
    #[derive(ToSchema, Serialize)]
    struct Order {
        id: i32,
        name: String,
    }

    #[derive(ToSchema, Deserialize, Serialize)]
    struct OrderRequest {
        name: String,
    }

    /// expose the Order OpenAPI to parent module
    pub fn router() -> OpenApiRouter<crate::RouterState> {
        OpenApiRouter::new().routes(routes!(get_order, create_order))
    }

    /// Get static order object
    #[utoipa::path(get, path = "", responses((status = OK, body = Order)), tag = super::ORDER_TAG)]
    async fn get_order() -> Json<Order> {
        Json(Order {
            id: 100,
            name: String::from("Bill Book"),
        })
    }

    /// Create an order.
    ///
    /// Create an order by basically passing through the name of the request with static id.
    #[utoipa::path(post, path = "", responses((status = OK, body = Order)), tag = super::ORDER_TAG)]
    async fn create_order(Json(order): Json<OrderRequest>) -> Json<Order> {
        Json(Order {
            id: 120,
            name: order.name,
        })
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
