## Twitch Setup

1. Add `http://localhost:PORT/twitch-callback/` as an OAuth Redirect URL. (Note the trailing slash, this is required)

## Local Environment Setup

Copy `.env_sample` to `.env`

Fill in values for:

- TWITCH_APP_ID (The Twitch Client ID you just generated)
- TWITCH_CLIENT_SECRET (The Twitch Client Secret you just generated)
- SUPERUSER (your twitch login username)
- POSTGRES_PW Root Password
- PORT - If you want to change the port TAU runs on, set `PORT` to this value.

## Docker Build

```bash
docker-compose up
```
