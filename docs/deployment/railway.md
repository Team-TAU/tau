# Railway Deployment

[Railway](https://railway.app/) is a cost effective way to run TAU 24/7 in the cloud. The following steps should get you started! These instructions assume you have cloned the TAU repo to your local drive, and that you have npm installed (the railway CLI app requires npm).

<!-- [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2FTeam-TAU%2Ftau%2Ftree%2Fdocumentation-railway-docs&plugins=postgresql%2Credis&envs=TWITCH_CLIENT_ID%2CTWITCH_CLIENT_SECRET%2CTWITCH_WEBHOOK_SECRET%2CDJANGO_DB_PW%2CDJANGO_SECRET_KEY%2CDJANGO_CONFIGURATION%2CPORT&TWITCH_CLIENT_IDDesc=Your+Twitch+TAU+app+id.&TWITCH_CLIENT_SECRETDesc=Your+Twitch+TAU+client+secret.&TWITCH_WEBHOOK_SECRETDesc=Random+string+of+10-100+characters.&DJANGO_DB_PWDesc=A+password+you+would+like+to+use+for+your+TAU+postgres+database.&DJANGO_SECRET_KEYDesc=Random+string+of+10-100+characters.&DJANGO_CONFIGURATIONDesc=DO+NOT+CHANGE&PORTDesc=DO+NOT+CHANGE&DJANGO_CONFIGURATIONDefault=Railway&PORTDefault=443&referralCode=TAU) -->

1. [Create a railway account/login](https://railway.app/login)
1. [Go to your railway dashboard](https://railway.app/dashboard)
1. Click "+ New Project" and select "Empty Project"
1. Click "+ New" in the upper right, and select "Database" --> "Add PostgreSQL"
1. Click "+ New" in the upper right, and select "Database" --> "Add Redis"
1. Click "+ New" in the upper right, and select "Empty Service"
1. Click on the new empty service which was just created.
1. Click the "Settings" tab, then under "Service" change the "Service Name" to something similar to `tau-twitchusername` using your Twitch username
1. In the same "Settings" tab under the "Environment > Domains", click the "Generate Domain" button. A new URL will be generated for you. You can edit this URL as you'd like. Note this domain, as it will be required in your environment variables, used when setting up TAU in the twitch dev dashboard, and the URL you will access the TAU Dashboard from.
1. [Get a Twitch Client ID and Client Secret](./twitch_dev.md). NOTE- rather than `http://localhost:PORT/twitch-callback/` as your OAuth redirect URL, you must use https and the domain you set up in the prior step without a port. E.g.: `https://tau-twitchname.up.railway.app/twitch-callback/`.
1. To add environment variables to the new Empty Service, copy the sample `.env` data below. Back in the Empty Service you created, under the "Variables" section, click "RAW Editor", and paste in the sample `.env` data and fill out with required information and save. After, close the service panel (x in the upper right corner of the panel)
1. Open a local terminal, navigate to your TAU root directory, and install the railway CLI using npm: `npm i -g @railway/cli` then login to railway: `railway login`
1. In your railway project dashboard, click on "Set up your project locally" in the lower left. Copy the link command with your projects UUID (something like: `railway link SOME-UUID-HERE`)
1. Back in the terminal paste/run the link command.
1. In the terminal, spin up your railway TAU instance (from the root TAU directory) with the command: `railway up`.
1. After the container spins up, navigate to your projects url, and complete the setup wizard. Note- it can take a few minutes for everything to spin up. When you navigate to your project url, you may see a warning that the project is spinning up or isn't connecting properly. Be patient, and it should start working in a couple minutes.
1. You're now running TAU on Railway!

## Sample .env data.

All `.env` data should come from your local install of TAU (see your existing `.env`). The first 6 values must be set. `TWITCH_CLIENT_ID` and `TWITCH_CLIENT_SECRET` come from the Twitch developer settings above, `TWITCH_WEBHOOK_SECRET` should be a random string of characters 10-100 characters long. `DJANGO_DB_PW` can be any password you want to set for the Django databse user, `DJANGO_SECRET_KEY` should be a different random string of characters 10-100 characters long, and `PUBLIC_URL` should be the deployment domain, e.g.- `tau-twitchname.up.railway.app`. The last two values (`DJANGO_CONFIGURATION` and `PORT`) should use the provided values below.

```
TWITCH_CLIENT_ID=
TWITCH_CLIENT_SECRET=
TWITCH_WEBHOOK_SECRET=
DJANGO_DB_PW=
DJANGO_SECRET_KEY=
PUBLIC_URL=
DJANGO_CONFIGURATION=Railway
PORT=443
```

## Connecting to Websockets

Now that TAU is deployed, you can connect to it via websockets at `wss://tau-twitchname.up.railway.app:443/ws/twitch-events/` using your new deployment domain. Also note that `wss` times out after about 10 minutes, so you will need to add a disconnect listener in your consuming application to reconnect each time the websocket times out.
