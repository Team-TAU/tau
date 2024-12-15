use log::{debug, error, info, trace, warn};
use std::{sync::Arc, time::Duration};

use chrono::{DateTime, Utc};
use futures_util::{pin_mut, StreamExt};
use serde::{Deserialize, Serialize};
use serde_json::json;
use sqlx::types::JsonValue;
use tokio::sync::mpsc;
use tokio::time::timeout;
use twitch_oauth2::AccessToken;
use uuid::Uuid;

use crate::RouterState;
use tokio_tungstenite::connect_async;

const EVENTSUB_URL: &str = "wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=30";
const ADDSUB_URL: &str = "https://api.twitch.tv/helix/eventsub/subscriptions";

#[derive(Serialize, Deserialize)]
struct MessageMetadata {
    message_id: String,
    message_type: String,
    message_timestamp: DateTime<Utc>,
    subscription_type: Option<String>,
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
    http_client: reqwest::Client,
}

impl EventSubWebSocket {
    pub fn new(state: Arc<RouterState>) -> Self {
        Self {
            state: state.clone(),
            http_client: reqwest::Client::new(),
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
                        warn!("we got a reconnect message");
                        if let Some(val) = val {
                            url = val;
                        }
                        break;
                    }
                    _ = &mut thing2 => {
                        warn!("Websocket closed. Retrying in 5 seconds...");
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
        let access_token = self
            .state
            .kv
            .refresh_access_token(&self.state.config, &self.state.pool)
            .await?;
        let (ws_stream, _) = connect_async(url.as_str()).await?;
        info!("EventSub WebSocket opened");
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
                    let Ok(msg) = serde_json::from_slice::<Message>(&data) else {
                        break;
                    };
                    self.process_message(msg, &reconnect, &url, &access_token)
                        .await?;
                }
            }
        }
        Ok(())
    }

    async fn process_message(
        &self,
        msg: Message,
        reconnect: &mpsc::Sender<String>,
        url: &str,
        access_token: &AccessToken,
    ) -> anyhow::Result<()> {
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
                use crate::events::Event;
                let event = Event {
                    id: Uuid::new_v4(),
                    event_id: Some(msg.metadata.message_id),
                    event_source: "EventSub".into(),
                    origin: Some("twitch".into()),
                    event_type: msg.metadata.subscription_type.unwrap().replace(".", "-"),
                    created: chrono::offset::Utc::now(),
                    event_data: msg
                        .payload
                        .get("event")
                        .ok_or(anyhow::anyhow!("twitch broke"))?
                        .clone(),
                };
                let result = sqlx::query!(
                    "INSERT INTO twitchevents_twitchevent
                            (id, event_id, event_type, event_source, event_data, created) VALUES
                            ($1, $2, $3, $4, $5, $6)",
                    event.id,
                    event.event_id,
                    event.event_type,
                    event.event_source,
                    event.event_data,
                    event.created
                )
                .execute(&self.state.pool)
                .await;
                if let Err(err) = result {
                    error!("ERROR: {}", err);
                }
                self.state.broadcast_event.send(event).unwrap();
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

                // This means we are in a reconnect scenario;
                // no need to resubscribe to our events.
                if EVENTSUB_URL != url {
                    return Ok(());
                }
                let subscriptions = sqlx::query!(
                    "SELECT
                        name,
                        version
                    FROM twitch_twitcheventsubsubscription
                    WHERE active = True"
                )
                .fetch_all(&self.state.pool)
                .await?;

                for sub in subscriptions.iter() {
                    let conditions = match sub.name.as_str() {
                        // raids are a special case - the same event
                        // is used for incoming and outgoing raids, so
                        // we have to subscribe twice with different conditions
                        // to capture all of the events.
                        "channel.raid" => {
                            vec![
                                json!({
                                    "from_broadcaster_user_id": self.state.kv.get_channel_id(),
                                }),
                                json!({
                                    "to_broadcaster_user_id": self.state.kv.get_channel_id(),
                                }),
                            ]
                        }
                        _ => {
                            let mut condition = json!({});
                            let spec = self
                                .state
                                .spec
                                .event_sub
                                .iter()
                                .find(|spec| spec.name == sub.name)
                                .ok_or(anyhow::anyhow!(
                                    "could not find spec for {} v{}",
                                    sub.name,
                                    sub.version
                                ))?;
                            for required in spec.condition_schema.required.iter() {
                                condition[required] = self.state.kv.get_channel_id().into();
                            }
                            vec![condition]
                        }
                    };

                    for condition in conditions {
                        let request = SubscriptionRequest {
                            sub_type: sub.name.to_string(),
                            version: sub.version.to_string(),
                            condition,
                            transport: Transport {
                                method: "websocket".to_string(),
                                session_id: id.to_string(),
                            },
                        };
                        let req = self
                            .http_client
                            .post(ADDSUB_URL)
                            .header("Authorization", format!("Bearer {}", access_token.secret()))
                            .header("Content-Type", "application/json")
                            .header("Client-Id", &self.state.config.twitch_app_id)
                            .body(serde_json::to_string(&request).unwrap())
                            .send()
                            .await;
                        match req {
                            Ok(res) => {
                                if !res.status().is_success() {
                                    error!(
                                        "Error subscribing to {} v{}\n{:?}",
                                        sub.name,
                                        sub.version,
                                        res.text().await.unwrap()
                                    );
                                } else {
                                    info!("Subscribed to {} v{}", sub.name, sub.version);
                                }
                            }
                            Err(err) => {
                                error!("Error subscribing: {:?}", err);
                            }
                        }
                    }
                }
            }
            _ => {}
        };
        Ok(())
    }
}
