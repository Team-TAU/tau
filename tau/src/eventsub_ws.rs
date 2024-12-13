use std::future::Future;
use std::{sync::Arc, time::Duration};

use chrono::{DateTime, Utc};
use futures_util::future::OptionFuture;
use futures_util::{pin_mut, StreamExt};
use serde::ser::Error;
use serde::{Deserialize, Serialize};
use serde_json::json;
use sqlx::types::JsonValue;
use tokio::net::unix::pipe::Sender;
use tokio::sync::mpsc;
use tokio::time::timeout;

use crate::RouterState;
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

pub struct EventSubWebSocket {
    state: Arc<RouterState>,
}

impl EventSubWebSocket {
    pub fn new(state: Arc<RouterState>) -> Self {
        Self {
            state: state.clone(),
        }
    }

    pub async fn run_loop(&self) {
        let mut url: String = EVENTSUB_URL.to_string();
        let (tx, mut rx) = mpsc::channel::<String>(10);
        loop {
            let thing2 = self.connect_websocket(url.clone(), tx.clone());
            url = EVENTSUB_URL.to_string();
            tokio::pin!(thing2);
            loop {
                tokio::select! {
                    val = rx.recv() => {
                        println!("we got a reconnect message");
                        if let Some(val) = val {
                            url = val;
                        }
                        println!("ok let's get rid of that old thing");
                        break;
                    }
                    _ = &mut thing2 => {
                        println!("our websocket died of natural causes");
                        println!("Websocket closed. Retrying in 5 seconds...");
                        tokio::time::sleep(std::time::Duration::from_millis(5000)).await;
                        break;
                    }
                };
            }
        }
    }

    async fn connect_websocket(
        &self,
        url: String,
        reconnect: mpsc::Sender<String>,
    ) -> anyhow::Result<()> {
        println!("websocket thread");
        let http_client = reqwest::Client::new();
        let access_token = self
            .state
            .kv
            .refresh_access_token(&self.state.config, &self.state.pool)
            .await?;
        // println!("Access token: {}", access_token.secret());
        let (ws_stream, _) = connect_async(url.as_str()).await?;
        println!("WebSocket handshake has been successfully completed");
        let (_write, read) = ws_stream.split();
        pin_mut!(read);

        // process incoming messages
        loop {
            match timeout(Duration::from_secs(60), read.next()).await {
                Ok(Some(Err(_))) | Err(_) | Ok(None) => {
                    break;
                }
                Ok(Some(Ok(message))) => {
                    let data = message.into_data();
                    if data.is_empty() {
                        continue;
                    }
                    // println!("Data: '{}'", String::from_utf8(data.clone()).unwrap());
                    let Ok(msg) = serde_json::from_slice::<Message>(&data) else {
                        break;
                    };
                    match msg.metadata.message_type.as_str() {
                        "session_reconnect" => {
                            let reconnect_url = msg
                                .payload
                                .get("session")
                                .ok_or(anyhow::anyhow!("twitch broke"))?
                                .get("reconnect_url")
                                .ok_or(anyhow::anyhow!("twitch broke"))?
                                .as_str()
                                .ok_or(anyhow::anyhow!("twitch broke"))?;
                            let _ = reconnect.send(reconnect_url.to_string()).await;
                        }
                        "notification" => {
                            println!("Data: '{}'", String::from_utf8(data.clone()).unwrap());
                        }
                        "session_keepalive" => {}
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
                                    "broadcaster_user_id": self.state.kv.get_channel_id(),
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
                            // println!("{}\n", serde_json::to_string(&request).unwrap());

                            // This means we are in a reconnect scenario;
                            // no need to resubscribe to our events.
                            if EVENTSUB_URL != url {
                                continue;
                            }
                            let req = http_client
                                .post(ADDSUB_URL)
                                .header(
                                    "Authorization",
                                    format!("Bearer {}", access_token.secret()),
                                )
                                .header("Content-Type", "application/json")
                                .header("Client-Id", &self.state.config.twitch_app_id)
                                .body(serde_json::to_string(&request).unwrap())
                                .send()
                                .await;
                            // println!("{:?}", req);
                            // println!("{:?}", req.unwrap().text().await.unwrap());
                        }
                        _ => {}
                    }
                }
            }
        }
        println!("i am dead now");
        Ok(())
    }
}
