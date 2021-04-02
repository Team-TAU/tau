# TAU - Twith API Unifier.

TAU provides a single, locally-managed websocket connection for
all of Twitch's realtime APIs. Currently the Twitch realtime
APIs are broken up into EventSub's WebHooks and PubSub's WebSockets.
In order to obtain all of the realtime events a typical Twitch bot or
overlay would use requires setting up multiple protocal, both server-side
(WebHooks) and client-side (WebSocket) messaging. It also requires
keeping track of multiple Twitch access tokens. TAU takes care of all
this for you, and adds the ability to replay past events and generate
test events of your own. Additionally, all events are stored in a
database.

Setting up TAU only takes a few minutes, and provides you with that
one true source of Twitch realtime API goodness. Please see the
setup instructions below.

_Note 1- TAU is very early stage software. There may be potential bugs
and even security issues. I am very open to PRs and discussions that
will help TAU become more stable and secure. Use at your own risk._

_Note 2- TAU is written using django/python, however, acting as an
API proxy, you can connect any codebase to its websockets._

# Prerequisites

- [docker-compose](https://docs.docker.com/compose/install/)
- A Twitch App Token and Secret (see getting started below)

# Getting Started

Before running TAU, it is necessary to obtain a Twitch App ID and
secret. In order to do so:

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

Now that you've obtained your Client ID and Client Secret, it is time to set up your `.env` file. I have included a `.env_sample` file. Copy this file to `.env`, and edit it. Values that
need to be edited are indicated by angle brackets. Fill in values for:

- Postgres Root Password
- TAU Database Password
- Django Secret Key (a random string)
- Twitch Webhook Secret (a random string)
- Twitch App ID (The Client ID you just generated)
- Twith Client Secret (The Client Secret you just generated)
  You probably will never need to use the Postgres and TAU database passwords, but you do need to set them to something (preferably a strong PW) in order to build the containers. 
- If you want to change the port TAU runs on (`PORT` in the steps above), set `TAU_PORT` to this value.
- The internal address is set to `0.0.0.0`, in order to allow incoming connections on the host machine to properly point to the server.
- If you want to use an existing ngrok account, set `USE_NGROK_TOKEN=True`, and `NGROK_TOKEN=<YOUR NGROK TOKEN>`

Please leave the other values alone, unless you know what you're doing.

Now that you've set up your `.env` file, open your terminal of choice, navigate to the TAU project directory (where you will find docker-compose.yml and Dockerfile), and execute the command

```bash
docker-compose up
```

If all goes to plan, you should see indications that the containers `tau-db`, `tau-redis`, and `tau-app` have started up, and you should see some logging output on your screen. In order to shut down the container, simply hit `ctrl-c`.  For future runs, you simply need to execute the `docker-compose up` command, as all of your settings will be saved.

At the very end of the logs in your terminal, you should see an indication that wsworker and server have entered a RUNNING state. At this point fire up a browser window and navigate to `http://localhost:PORT` . A wizard will guide you through setting up your TAU user account (this is only stored on your local container), have you enter your Twitch Channel Name, and then will have you authorize TAU to have access to your realtime data. After providing authorization, you will be sent back to a dashboard which shows both the current realtime connection status, as well as a real-time monitoring of your client-side websocket.

To connect your bot or overlay code to TAU, you will need a TAU auth token.  This can be obtained by clicking the hamberger icon in the TAU dashboard, then clicking "Show Auth Token."

Then simply point your bot's websocket client at `ws://localhost:PORT/ws/twitch-events/` .  After it connects, send a websocket message from the client with the following JSON payload: `{"token": "YOUR_TOKEN HERE"}`.  After providing your token, TAU will begin to stream all twitch events to your websocket connection.  Fin.

# Updating

After pulling the latest code from github, you will need to rebuild the app container before re-launching TAU.  You can do so as follows:

1. If TAU is running, stop it using `docker-compose down`
2. Rebuild the app container: `docker-compose build app`
3. Fire TAU back up: `docker-compose up`

# Todo/Issues

Currently, while hypetrain events are forwarded on to any local clients connected to the TAU websocket connection, they are not shown in the TAU dashboard, nor do they have test events available.
