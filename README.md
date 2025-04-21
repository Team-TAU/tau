# TAU - Twitch API Unifier

Making integrations with Twitch API easier than ever!

# Recent Changes

TAU has been rewritten in rust. Upgrading to this new version **will break backwards compatibility** with previous versions of TAU. Because of this, it is strongly recommended to make a backup of your database before upgrading.

# Table of Contents

- [Introduction](#microphone-introduction)
- [Features](#star-features)
- [Prerequisites](#white_check_mark-prerequisites)
- [Getting Started](#gear-getting-started)
- [Updating](#hourglass_flowing_sand-updating)
- [Todo/Issues](#thought_balloon-todoissues)

# :microphone: Introduction

TAU provides a single, locally-managed websocket connection for
all of Twitch's [EventSub](https://dev.twitch.tv/docs/eventsub) API.

TAU adds the ability to replay past events and generate
test events of your own from a user friendly UI. Additionally, all events are stored in a
database.

Setting up TAU only takes a few minutes, and provides you with that
one true source of Twitch realtime API goodness. Please see the
setup instructions below.

_Note 1- TAU is very early stage software. There may be potential bugs
and even security issues. I am very open to PRs and discussions that
will help TAU become more stable and secure. Use at your own risk._

_Note 2- TAU is written using rust, however, acting as an
API proxy, you can connect any codebase to its websocket._

_Note 3- If when starting up TAU, you see the error:
```
 bash: ./scripts/start.sh: /bin/bash^M: bad interpreter: No such file or directory
```
This is due to windows git changing your line endings from `lf` to `crlf`.  Use the command:
```
git config --global core.autocrlf input
```
Turn off autoclrf, and re-clone the repository.

# :star: Features

- Easy to use UI to manage Twitch events
  - Enable or Disable events
  - Test events
  - Replay Events
- Containerized setup for ease of spinning up and teardown
- Exposes 1 websocket for all Twitch Events

# :white_check_mark: Prerequisites

- [docker-compose](https://docs.docker.com/compose/install/)
- [Twitch Account](https://twitch.tv)

# :gear: Getting Started

First thing you'll need to do is to clone or download this repo to a local folder.

## Twitch Setup

Because TAU depends heavily on Twitch, it is necessary to obtain a Twitch Client ID and Client Secret. The steps below will help you do this.

1. Determine the port you want to run TAU on. By default this is port 8000. Use this value for `PORT` in the following steps.
1. Visit the [Twitch Developer Applications Console](https://dev.twitch.tv/console/apps).
1. Log in to your Twitch account if you are not already logged in.
1. In order to manage applications, you will need to enable 2FA for your account.
1. Click "+ Register Your Application".
1. Fill in a name for TAU. I recommend TAU- YourTwitchName.
1. Add `http://localhost:PORT/twitch-callback/` as an OAuth Redirect URL. (Note the trailing slash, this is required)
1. Add `http://localhost:PORT/api/v1/chat-bots/twitch-callback/` as a second OAuth Redirect URL. (Note the trailing slash, this is required)
1. Select a category for what you'll be using TAU for. Chat Bot is what I've used.
1. Click "Create"
1. Click "Manage" for the TAU app.
1. Here is where you can find your Client ID, and generate a Client Secret. You'll need these two values later. Note- you can only see the client secret when you generate it, so make sure you copy it to put in your .env file later. Dont worry if you lose it, you can always generate a new secret.

## :house_with_garden: Local Environment Setup

Now that you've obtained your Client ID and Client Secret, it is time to set up your `.env` file. I have included a `.env_sample` file. Copy this file and rename to `.env`.

Fill in values for:

- TWITCH_CLIENT_ID (The Twitch Client ID you just generated)
- TWITCH_CLIENT_SECRET (The Twitch Client Secret you just generated)
- TWITCH_WEBHOOK_SECRET (a random string)
- POSTGRES_PW Root Password
- PORT - If you want to change the port TAU runs on, set `PORT` to this value.

Note- You probably will never need to use the Postgres password but you do need to set them to something (preferably a strong PW) in order to build the containers.

Please leave any other values alone, unless you know what you're doing. 😊

## :whale: Docker Build

Now that you've set up your `.env` file, open your terminal of choice, navigate to the TAU project directory (where you will find docker-compose.yml and Dockerfile), and execute the command

```bash
docker-compose up
```

If all goes to plan, you should see indications that the containers `tau-db` and `tau-app` have started up, and you should see some logging output on your screen. In order to shut down the container, simply hit `ctrl-c`. For future runs, you simply need to execute the `docker-compose up` command, as all of your settings will be saved.

At the very end of the logs in your terminal, you should see an indication that wsworker and server have entered a RUNNING state (about 10 lines from the bottom).

## TAU Setup

At this point fire up a browser window and navigate to `http://localhost:PORT` . A wizard will guide you through setting up your TAU user account. This data is only stored on your local container. Create a username and password then enter your Twitch Channel Name and click `Setup Channel`. You will then be prompted to authorize TAU access to your Twitch realtime data. After providing authorization, you will be sent to a dashboard which shows both the current realtime connection status, as well as a real-time monitoring of your client-side websocket.

## :robot: Bot Integration

To connect your bot or overlay code to TAU, you will need a TAU auth token. This can be obtained by clicking the hamburger icon in the TAU dashboard, then clicking "Show Auth Token."

Then simply point your bot's websocket client at `ws://localhost:PORT/ws/twitch-events/`. After it connects, send a websocket message from the client with the following JSON payload: `{"token": "YOUR_TOKEN HERE"}`. After providing your token, TAU will begin to stream all Twitch events to your websocket connection. Fin!

# :hourglass_flowing_sand: Updating

In order to update TAU, pull/download the latest code from github. You will then need to rebuild the app container before re-launching TAU. You can do so as follows:

1. Destroy the containers: `docker compose down`
2. Fire TAU back up by rebuilding the containers: `docker compose up --build`
