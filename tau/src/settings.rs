use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct Settings {
    pub twitch_client_secret: String,
    pub twitch_app_id: String,
    pub superuser: String,
}
