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
        .with_state(state)
        .routes(routes!(health))
        .nest("/api/v1/auth", auth::router())
        .nest("/api/v1/customer", customer::router())
        .nest("/api/v1/order", order::router())
        .routes(routes!(
            inner::secret_handlers::get_secret,
            inner::secret_handlers::post_secret
        ))
        .split_for_parts();

    let router = router.merge(SwaggerUi::new("/swagger-ui").url("/apidoc/openapi.json", api));

    let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 3000)).await?;
    axum::serve(listener, router).await?;
    Ok(())
}

mod auth {
    use axum::http::StatusCode;
    use axum::response::IntoResponse;
    use axum::Json;
    use serde::Serialize;
    use utoipa::ToSchema;
    use utoipa_axum::router::OpenApiRouter;
    use utoipa_axum::routes;

    #[derive(ToSchema, Serialize)]
    struct TokenResponse {
        token: String,
    }

    pub fn router() -> OpenApiRouter {
        OpenApiRouter::new().routes(routes!(post_token_auth))
    }

    #[utoipa::path(post, path = "/token", responses(
        (status = OK, body = TokenResponse),
        (status = FORBIDDEN, body = ())
    ), tag = super::AUTH_TAG)]
    async fn post_token_auth() -> impl IntoResponse {
        if
        (
            StatusCode::OK,
            Json(TokenResponse {
                token: String::from("thisisyourtoken"),
            }),
        )
        (
            StatusCode::OK,
            Json(TokenResponse {
                token: String::from("thisisyourtoken"),
            }),
        )
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
    pub fn router() -> OpenApiRouter {
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
    pub fn router() -> OpenApiRouter {
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
