use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct Settings {
    pub twitch_client_secret: String,
    pub twitch_app_id: String,
    pub superuser: String,
    pub public_read_access: bool,
    pub initial_migration: bool,
    pub postgres_connection: String,
    pub base_url: String,
    pub port: u16,
}
