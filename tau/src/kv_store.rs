use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::{Pool, Postgres};
use std::io::{Read, Write};
use std::process::{Command, Stdio};

#[derive(Serialize, Deserialize, Clone)]
pub enum KVKey {}

#[derive(Clone, Serialize, Deserialize, Default)]
pub struct KVStore {
    pub channel: String,
    pub twitch_app_access_token: String,
    pub scope_updated_needed: bool,
    pub reset_all_webhooks: bool,
    pub scopes_refreshed: bool,
    pub channel_id: String,
    pub use_irc: bool,
    pub twitch_refresh_token: String,
    pub twitch_access_token: String,
    pub twitch_access_token_expiration: DateTime<Utc>,
}

#[derive(Serialize, Deserialize, Clone)]
struct MigrationRow {
    key: String,
    value: String,
    id: u32,
}

impl KVStore {
    pub fn new() -> Self {
        return Self::default();
    }

    pub async fn load(&mut self, pool: &Pool<Postgres>) -> Result<(), anyhow::Error> {
        let row = sqlx::query!("SELECT data FROM kv_store",)
            .fetch_one(pool)
            .await?
            .data
            .ok_or(anyhow::anyhow!("Failed to load KV store"))?;
        *self = serde_json::from_str(row.as_str())?;
        Ok(())
    }

    pub async fn save(&self, pool: &Pool<Postgres>) -> Result<(), anyhow::Error> {
        sqlx::query!(
            "INSERT INTO kv_store (data)
VALUES ($1)
ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data",
            serde_json::to_string(&self).unwrap()
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
            *self = serde_json::from_str(&output)?;
            Ok(())
        } else {
            Err(anyhow::anyhow!("Python script failed to execute"))
        }
    }
}
