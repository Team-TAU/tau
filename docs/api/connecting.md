# Connecting To TAU
TAU provides two different APIs-

1. A websocket that broadcasts realtime Twitch events, test events, and replayed events.
2. A REST API the provides access to a passthrough of the Twitch Helix API, as well as endpoints for accessing the data captured and stored by TAU.

## Getting your TAU token.
A TAU token is required for both the realtime websocket API and the REST API.  To obtain your token, go to the TAU Dashboard, click the hamburger menu, then click `Show Auth Token`

## Connecting to the realtime websocket.
TAU exposes a websocket endpoint at `ws://localhost:PORT/ws/twitch-events/` for a local deployment or `wss://yourdomain:PORT/ws/twitch-events/` for a served deployment.  After connecting your client to the websocket, you must send a message containing the following json object:
```
{ 
    "token": "YOUR TAU TOKEN HERE"
}
```
After receiving your token, TAU will begin to broadcast incoming twitch events to your client.

## Connecting to the REST API
TAU also provides 2 separate REST APIs.  A passthrough of the Twitch Helix API at: `/api/twitch/helix`, and access to the data captured and stored by TAU at `/api/v1`.  In order to authenticate requests, you must include an Authorization header:
```
Authorization: Token YOUR-TAU-TOKEN-HERE
```
The Update Token Scopes page from the dashboard will allow you to add scopes to the Twitch token used by TAU.

## Connecting to Chat Bot Websockets
TAU also provides websockets for your streamer user chat, and any chat bots you have set up at `ws/chat-bots/<chat-bot-username>/` where `<chat-bot-username>` is the all-lowercase twitch username of your streamer account or any chat-bot accounts you have set up in TAU.

After connecting your client to the websocket, you must send a message containing the following json object:

```
{ 
    "token": "YOUR TAU TOKEN HERE"
}
```

After receiving your token, TAU will begin to broadcast incoming twitch chat events to your client.  You can also send outgoing messages to be posted in chat by your bot.  Simply send the following payload to the endpoint of the bot you would like to have "speak":

```
{
    "irc_channel": "channel_to_send_to",
    "message": "message to post in channel."
}
```
