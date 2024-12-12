use std::sync::Arc;

use chrono::{DateTime, Utc};
use futures_util::{future, pin_mut, StreamExt};
use serde::{Deserialize, Serialize};
use serde_json::json;
use sqlx::types::JsonValue;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

use tokio_tungstenite::connect_async;

const EVENTSUB_URL: &str = "wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=30";
const ADDSUB_URL: &str = "https://api.twitch.tv/helix/eventsub/subscriptions";

#[derive(Serialize, Deserialize)]
struct MessageMetadata {
    message_id: String,
    message_type: String,
    message_timestamp: DateTime<Utc>,
}

#[derive(Serialize, Deserialize)]
struct Message {
    metadata: MessageMetadata,
    payload: JsonValue,
}

#[derive(Serialize, Deserialize)]
struct Transport {
    session_id: String,
    method: String,
}

#[derive(Serialize, Deserialize)]
struct SubscriptionRequest {
    #[serde(rename = "type")]
    sub_type: String,
    version: String,
    transport: Transport,
    condition: JsonValue,
}

use crate::RouterState;
pub async fn eventsub_websocket(state: Arc<RouterState>) -> anyhow::Result<()> {
    println!("websocket thread");
    let http_client = reqwest::Client::new();
    let access_token = state
        .kv
        .refresh_access_token(&state.config, &state.pool)
        .await?;
    println!("Access token: {}", access_token.secret());
    let (ws_stream, _) = connect_async(EVENTSUB_URL).await?;
    println!("WebSocket handshake has been successfully completed");
    let (write, read) = ws_stream.split();
    pin_mut!(read);
    while let Some(Ok(message)) = read.next().await {
        let data = message.into_data();
        if data.is_empty() {
            continue;
        }
        println!("Data: '{}'", String::from_utf8(data.clone()).unwrap());
        let Ok(msg) = serde_json::from_slice::<Message>(&data) else {
            break;
        };
        match msg.metadata.message_type.as_str() {
            "session_welcome" => {
                let id = msg
                    .payload
                    .get("session")
                    .ok_or(anyhow::anyhow!("twitch broke"))?
                    .get("id")
                    .ok_or(anyhow::anyhow!("twitch broke"))?
                    .as_str()
                    .ok_or(anyhow::anyhow!("twitch broke"))?;
                println!("got your id {}", id);
                let request = SubscriptionRequest {
                    sub_type: "channel.ban".to_string(),
                    version: "1".to_string(),
                    condition: json!({
                        "broadcaster_user_id": state.kv.get_channel_id(),
                    }),
                    transport: Transport {
                        method: "websocket".to_string(),
                        session_id: id.to_string(),
                    },
                };
                // let req = http_client
                //     .get("https://id.twitch.tv/oauth2/validate")
                //     .header("Authorization", format!("Bearer {}", access_token.secret()))
                //     .send()
                //     .await?;
                // println!("{:?}", req.text().await.unwrap());
                println!("{}\n", serde_json::to_string(&request).unwrap());
                let req = http_client
                    .post(ADDSUB_URL)
                    .header("Authorization", format!("Bearer {}", access_token.secret()))
                    .header("Content-Type", "application/json")
                    .header("Client-Id", &state.config.twitch_app_id)
                    .body(serde_json::to_string(&request).unwrap())
                    .send()
                    .await;
                println!("{:?}", req);
                println!("{:?}", req.unwrap().text().await.unwrap());
            }
            _ => {}
        }
    }
    println!("WebSocket closed");
    Ok(())
}
