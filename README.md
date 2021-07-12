# TAU - Twitch API Unifier

Making integrations with Twitch API easier than ever!

<!-- Badges Start -->
[![API Docs: 5 Endpoints](https://img.shields.io/static/v1?label=API%20Docs&message=5%20Endpoints&style=flat&color=rgb(43%2C123%2C209)&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTM0IiBoZWlnaHQ9IjEzNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayI%2BPGRlZnM%2BPGxpbmVhckdyYWRpZW50IHgxPSI1MCUiIHkxPSItMTQuMyUiIHgyPSI1MCUiIHkyPSIxMDAlIiBpZD0iYyI%2BPHN0b3Agc3RvcC1jb2xvcj0iI0ZGRiIgb2Zmc2V0PSIwJSIvPjxzdG9wIHN0b3AtY29sb3I9IiNGNEY0RjQiIG9mZnNldD0iMTAwJSIvPjwvbGluZWFyR3JhZGllbnQ%2BPGZpbHRlciB4PSItNS42JSIgeT0iLTQlIiB3aWR0aD0iMTExLjElIiBoZWlnaHQ9IjExMS4xJSIgZmlsdGVyVW5pdHM9Im9iamVjdEJvdW5kaW5nQm94IiBpZD0iYSI%2BPGZlT2Zmc2V0IGR5PSIyIiBpbj0iU291cmNlQWxwaGEiIHJlc3VsdD0ic2hhZG93T2Zmc2V0T3V0ZXIxIi8%2BPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMiIgaW49InNoYWRvd09mZnNldE91dGVyMSIgcmVzdWx0PSJzaGFkb3dCbHVyT3V0ZXIxIi8%2BPGZlQ29sb3JNYXRyaXggdmFsdWVzPSIwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwLjUgMCIgaW49InNoYWRvd0JsdXJPdXRlcjEiLz48L2ZpbHRlcj48Y2lyY2xlIGlkPSJiIiBjeD0iNjMiIGN5PSI2MyIgcj0iNjMiLz48L2RlZnM%2BPGcgZmlsbD0ibm9uZSIgZmlsbC1ydWxlPSJldmVub2RkIj48ZyBmaWxsLXJ1bGU9Im5vbnplcm8iIHRyYW5zZm9ybT0idHJhbnNsYXRlKDQgMikiPjx1c2UgZmlsbD0iIzAwMCIgZmlsdGVyPSJ1cmwoI2EpIiB4bGluazpocmVmPSIjYiIvPjx1c2UgZmlsbD0idXJsKCNjKSIgeGxpbms6aHJlZj0iI2IiLz48L2c%2BPHBhdGggZD0iTTkwIDM1YTM4IDM4IDAgMDAtNDYgMG0yOCA2OGEzOCAzOCAwIDAwMzMtMzhjMC04LTMtMTYtNy0yMm0tMzYgNjBhMzggMzggMCAwMS0zMy0zOGMwLTggMy0xNiA3LTIyIiBzdHJva2U9IiMzNDNCRTUiIHN0cm9rZS13aWR0aD0iNC43IiBzdHJva2UtbGluZWNhcD0icm91bmQiLz48cGF0aCBkPSJNNTEgODVhMjYgMjYgMCAwMDMyIDBNNjMgMzljLTUgMS0xMCAzLTE0IDdhMjYgMjYgMCAwMC0zIDM0bTI1LTQxYzUgMSAxMCAzIDE0IDdhMjYgMjYgMCAwMTMgMzQiIHN0cm9rZT0iIzM0M0JFNSIgc3Ryb2tlLXdpZHRoPSI0LjciIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPjwvZz48L3N2Zz4%3D)](https://spec.useoptic.com/people/11e07ccb-9382-4968-b133-fc14c19e793e/public-specs/a0f4dd00-36ff-4c7c-b130-5b8a3c182b72/documentation)
<!-- Badges End -->

# Table of Contents
- [Introduction](#Introduction)
- [Features](#Features)
- [Prerequisites](#Prerequisites)
- [Getting Started](#Getting-Started)
- [Updating](#Updating)
- [Todo/Issues](#Todo/Issues)

# :microphone: Introduction

TAU provides a single, locally-managed websocket connection for
all of Twitch's realtime APIs. Currently, Twitch's realtime
APIs are broken up into [EventSub WebHooks](https://dev.twitch.tv/docs/eventsub) and [PubSub WebSockets](https://dev.twitch.tv/docs/pubsub).

In order for a Twitch bot or overlay to be interractive, it needs to tap into the realtime events sent over the Twitch APIs. This typically requires setting up multiple protocols: a webhook on the server-side and websockets on the client-side. It also requires you to keep track of multiple Twitch access tokens. This is where TAU comes in! TAU takes care of all
this for you and also adds the ability to replay past events and generate
test events of your own from a user friendly UI. Additionally, all events are stored in a
database.

Setting up TAU only takes a few minutes, and provides you with that
one true source of Twitch realtime API goodness. Please see the
setup instructions below.

_Note 1- TAU is very early stage software. There may be potential bugs
and even security issues. I am very open to PRs and discussions that
will help TAU become more stable and secure. Use at your own risk._

_Note 2- TAU is written using django/python, however, acting as an
API proxy, you can connect any codebase to its websockets._

 # :star: Features

- Easy to use UI to manage Twitch events
  - Enable or Disable events
  - Test events
  - Replay Events
- Containerized setup for ease of spinning up and teardown
- Manages multiple Twitch Event APIs without needing to register multiple Applications
- Exposes 1 websocket for all Twitch Events

# :white_check_mark: Prerequisites

- [docker-compose](https://docs.docker.com/compose/install/)
- [Twitch Account](https://twitch.tv)

# :gear: Getting Started

First thing you'll need to do is to clone or download this repo to a local folder.

## Twitch Setup
Because TAU depends heavily on Twitch, it is necessary to obtain a Twitch App ID and
secret. The steps below will help you do this.

1. Determine the port you want to run TAU on.  By default this is port 8000.  Use this value for `PORT` in the following steps.
1. Visit the [Twitch Developer Applications Console](https://dev.twitch.tv/console/apps).
2. Log in to your Twitch account if you are not already logged in.
3. In order to manage applications, you will need to enable 2FA for your account.
4. Click "+ Register Your Application".
5. Fill in a name for TAU. I recommend TAU- YourTwitchName.
6. Add `http://localhost:PORT/twitch-callback/` as an OAuth Redirect URL. (Note the trailing slash, this is required)
7. Select a category for what you'll be using TAU for. Chat Bot is what I've used.
8. Click "Create"
9. Click "Manage" for the TAU app.
10. Here is where you can find your Client ID, and generate a Client Secret. You'll need these two values later. Note- you can only see the client secret when you generate it, so make sure you copy it to put in your .env file later. Dont worry if you lose it, you can always generate a new secret.

## :house_with_garden: Local Environment Setup
Now that you've obtained your Client ID and Client Secret, it is time to set up your `.env` file. I have included a `.env_sample` file. Copy this file and rename to `.env`.

Fill in values for:
- TWITCH_APP_ID (The Twitch Client ID you just generated)
- TWITCH_CLIENT_SECRET (The Twitch Client Secret you just generated)
- TWITCH_WEBHOOK_SECRET (a random string)
- POSTGRES_PW Root Password
- DJANGO_DB_PW (a random string)
- DJANGO_SECRET_KEY (a random string)
- PORT - If you want to change the port TAU runs on, set `PORT` to this value.
- If you want to use an existing ngrok account, set `NGROK_TOKEN=<YOUR NGROK TOKEN>`

Note- You probably will never need to use the Postgres password but you do need to set them to something (preferably a strong PW) in order to build the containers. 

Please leave any other values alone, unless you know what you're doing. 😊

## :whale: Docker Build
Now that you've set up your `.env` file, open your terminal of choice, navigate to the TAU project directory (where you will find docker-compose.yml and Dockerfile), and execute the command

```bash
docker-compose up
```

If all goes to plan, you should see indications that the containers `tau-db`, `tau-redis`, and `tau-app` have started up, and you should see some logging output on your screen. In order to shut down the container, simply hit `ctrl-c`.  For future runs, you simply need to execute the `docker-compose up` command, as all of your settings will be saved.

At the very end of the logs in your terminal, you should see an indication that wsworker and server have entered a RUNNING state (about 10 lines from the bottom). 

## TAU Setup 
At this point fire up a browser window and navigate to `http://localhost:PORT` . A wizard will guide you through setting up your TAU user account. This data is only stored on your local container. Create a username and password then enter your Twitch Channel Name and click `Setup Channel`. You will then be prompted to authorize TAU access to your Twitch realtime data. After providing authorization, you will be sent to a dashboard which shows both the current realtime connection status, as well as a real-time monitoring of your client-side websocket.

## :robot: Bot Integration
To connect your bot or overlay code to TAU, you will need a TAU auth token. This can be obtained by clicking the hamburger icon in the TAU dashboard, then clicking "Show Auth Token."

Then simply point your bot's websocket client at `ws://localhost:PORT/ws/twitch-events/`.  After it connects, send a websocket message from the client with the following JSON payload: `{"token": "YOUR_TOKEN HERE"}`.  After providing your token, TAU will begin to stream all Twitch events to your websocket connection.  Fin!

>Note: If you wish to run TAU using a cloud service rather than locally, you will need to provide your own Redis server.  This can either be another container running in the cloud, or a Redis provider such as Redislabs.  Since Redis is used as a simple message broker, something like Redislab's free tier will be more than sufficient for most users.  Then, simply provide the `REDIS_ENDPOINT` and `REDIS_PW` environment variables.  Additionally, you will need to either provide a working postgres installation, or change the `DJANGO_DB_TYPE` environment variable to `sqlite3` to use django's local sqlite3 library.  See the .env_single_container_sample file.

# :hourglass_flowing_sand: Updating

In order to update TAU, pull/download the latest code from github. You will then need to rebuild the app container before re-launching TAU.  You can do so as follows:

1. Destroy the containers: `docker compose down`
2. Fire TAU back up by rebuilding the containers: `docker compose up --build`

# :thought_balloon: Todo/Issues

Currently, while hypetrain events are forwarded on to any local clients connected to the TAU websocket connection, they are not shown in the TAU dashboard, nor do they have test events available.
