# TAU

## Introduction
TAU provides a single, locally-managed websocket connection for all of Twitch's realtime APIs. Currently, Twitch's realtime APIs are broken up into EventSub WebHooks and PubSub WebSockets.

In order for a Twitch bot or overlay to be interractive, it needs to tap into the realtime events sent over the Twitch APIs. This typically requires setting up multiple protocols: a webhook on the server-side and websockets on the client-side. It also requires you to keep track of multiple Twitch access tokens. This is where TAU comes in! TAU takes care of all this for you and also adds the ability to replay past events and generate test events of your own from a user friendly UI. Additionally, all events are stored in a database.

