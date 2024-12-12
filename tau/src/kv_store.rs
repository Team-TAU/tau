use crate::settings::Settings;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::{Pool, Postgres};
use std::io::{Read, Write};
use std::mem::drop;
use std::process::{Command, Stdio};
use tokio::sync::{broadcast, Mutex};

#[derive(Default, Serialize, Deserialize)]
pub struct KVInner {
    pub channel: String,
    pub twitch_app_access_token: String,
    pub channel_id: String,
    pub use_irc: bool,
    pub twitch_refresh_token: String,
    pub twitch_access_token: String,
    pub twitch_access_token_expiration: DateTime<Utc>,
}

pub struct KVStore {
    data: std::sync::RwLock<KVInner>,
    refresh_handle: Mutex<Option<broadcast::Sender<()>>>,
}

#[derive(Serialize, Deserialize, Clone)]
struct MigrationRow {
    key: String,
    value: String,
    id: u32,
}

impl KVStore {
    pub fn new() -> Self {
        return KVStore {
            data: std::sync::RwLock::new(KVInner::default()),
            refresh_handle: Mutex::new(None),
        };
    }

    pub async fn refresh_access_token(&self, config: &Settings, pool: &Pool<Postgres>) {
        // TODO: check if we need to refresh in the first place
        let mut handle = self.refresh_handle.lock().await;
        if handle.is_some() {
            // if the token is already being refreshed, we
            // can just wait for that to happen
            let tx = handle.as_mut().unwrap();
            let mut rx = tx.subscribe();
            drop(handle);
            let _ = rx.recv().await;
        } else {
            let (tx, _rx) = broadcast::channel(1);
            *handle = Some(tx);
            drop(handle);
            // ok fine, let's start an async task to refresh the token
            println!(
                "before token: {}",
                self.data.read().unwrap().twitch_access_token
            );
            let current_refresh = self.data.read().unwrap().twitch_refresh_token.clone();
            let client_secret = config.twitch_client_secret.clone();
            let client_id = config.twitch_app_id.clone();
            let res = tokio::spawn(async {
                let refresh = twitch_oauth2::RefreshToken::from(current_refresh);
                let client = reqwest::Client::new();
                refresh
                    .refresh_token(&client, &client_id.into(), &client_secret.into())
                    .await
            })
            .await;
            if let Ok(Ok((access_token, duration, Some(refresh)))) = res {
                let mut data = self.data.write().unwrap();
                data.twitch_refresh_token = refresh.secret().to_string();
                data.twitch_access_token = access_token.secret().to_string();
                data.twitch_access_token_expiration = chrono::offset::Utc::now() + duration;
                drop(data);
            } else {
                println!("ERROR refreshing twitch token");
            }
            println!(
                "after token: {}",
                self.data.read().unwrap().twitch_access_token
            );
            let mut handle = self.refresh_handle.lock().await;
            *handle = None;
            drop(handle);
            let _ = self.save(pool).await;
        }
    }

    pub async fn load(&mut self, pool: &Pool<Postgres>) -> anyhow::Result<()> {
        let row = sqlx::query!("SELECT data FROM kv_store",)
            .fetch_one(pool)
            .await?
            .data
            .ok_or(anyhow::anyhow!("Failed to load KV store"))?;
        self.data = serde_json::from_str(row.as_str())?;
        Ok(())
    }

    pub async fn save(&self, pool: &Pool<Postgres>) -> anyhow::Result<()> {
        sqlx::query!(
            "INSERT INTO kv_store (data)
VALUES ($1)
ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data",
            serde_json::to_string(&self.data).unwrap()
        )
        .execute(pool)
        .await?;
        Ok(())
    }

    pub async fn migrate(&mut self, pool: &Pool<Postgres>) -> Result<(), anyhow::Error> {
        let row = sqlx::query!(
            "SELECT array_to_json(array_agg(row_to_json(constance_config))) as json_agg FROM constance_config",
        )
        .fetch_one(pool)
        .await
        .unwrap();

        let json = row.json_agg.unwrap();
        let mut child = Command::new("python3")
            .arg("migrate_constance.py")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit())
            .spawn()?;

        // Write data to the Python process's stdin
        if let Some(mut stdin) = child.stdin.take() {
            stdin.write_all(json.to_string().as_bytes())?;
        }

        // Read the output from the Python process's stdout
        let mut output = String::new();
        if let Some(mut stdout) = child.stdout.take() {
            stdout.read_to_string(&mut output)?;
        }

        let status = child.wait()?;

        // Check if the process succeeded
        if status.success() {
            self.data = serde_json::from_str(&output)?;
            Ok(())
        } else {
            Err(anyhow::anyhow!("Python script failed to execute"))
        }
    }
}
