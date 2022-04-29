# Railway Deployment

[Railway](https://railway.app/) is a cost effective way to run TAU 24/7 in the cloud. The following steps should get you started! These instructions assume you have cloned the TAU repo to your local drive, and that you have npm installed (the railway CLI app requires npm).

<!-- [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2FTeam-TAU%2Ftau%2Ftree%2Fdocumentation-railway-docs&plugins=postgresql%2Credis&envs=TWITCH_APP_ID%2CTWITCH_CLIENT_SECRET%2CTWITCH_WEBHOOK_SECRET%2CDJANGO_DB_PW%2CDJANGO_SECRET_KEY%2CDJANGO_CONFIGURATION%2CPORT&TWITCH_APP_IDDesc=Your+Twitch+TAU+app+id.&TWITCH_CLIENT_SECRETDesc=Your+Twitch+TAU+client+secret.&TWITCH_WEBHOOK_SECRETDesc=Random+string+of+10-100+characters.&DJANGO_DB_PWDesc=A+password+you+would+like+to+use+for+your+TAU+postgres+database.&DJANGO_SECRET_KEYDesc=Random+string+of+10-100+characters.&DJANGO_CONFIGURATIONDesc=DO+NOT+CHANGE&PORTDesc=DO+NOT+CHANGE&DJANGO_CONFIGURATIONDefault=Railway&PORTDefault=443&referralCode=TAU) -->

1. [Create a railway account/login](https://railway.app/login)
1. [Go to your railway dashboard](https://railway.app/dashboard)
1. Click "+ New Project" and select "Empty Project"
1. Click "+ New" in the upper right, and select "Database" --> "Add PostgreSQL"
1. Click "+ New" in the upper right, and select "Database" --> "Add Redis"
1. Click "+ New" in the upper right, and select "Empty Service"
1. Click on the new empty service which was just created.
1. Click the "Settings" tab under "Environment > Service Domains", edit the production domain to a url that you want (e.g.- tau-twitchname.up.railway.app). Note this domain, as it will be required in your environment variables, and when setting up TAU in the twitch dev dashboard.
1. [Get a Twitch Client ID and Client Secret](./twitch_dev.md). NOTE- rather than `http://localhost:PORT/twitch-callback/` as your OAuth redirect URL, you must use https, the domain you set up in the prior step, and no port. E.g.: `https://tau-twitchname.up.railway.app`.
1. Copy the sample `.env` data below, and paste in a text editor. Add values for the first six enviornment variables as explained below.
1. Back in the `Variables` section of your railway projects empty service, click `Bulk Import`, and paste in your edited .env data, and click `Add`. Then close the service panel (x in the upper right corner of the panel)
1. In a terminal install the railway CLI using npm: `npm i -g @railway/cli` then login to railway: `railway login`
1. In your railway project dashboard, click on "Set up your project locally" in the lower left. Copy the link command with your projects UUID (something like: `railway link SOME-UUID-HERE`)
1. In the terminal, navigate to the TAU root directory, and paste/run the link command.
1. In the terminal, spin up your railway TAU instance (from the root TAU directory) with the command: `railway up`.
1. After the container spins up, navigate to your projects url, and complete the setup wizard. Note- it can take a few minutes for everything to spin up. When you navigate to your project url, you may see a warning that the project is spinning up or isnt connecting properly. Be patient, and it should start working in a couple minutes.
1. You're now running TAU!

## Sample .env data.

The first 6 values must be set. `TWITCH_APP_ID` and `TWITCH_CLIENT_SECRET` come from the Twitch developer settings above, `TWITCH_WEBHOOK_SECRET` should be a random string of characters 10-100 characters long. `DJANGO_DB_PW` can be any password you want to set for the Django databse user, `DJANGO_SECRET_KEY` should be a different random string of characters 10-100 characters long, and `PUBLIC_URL` should be the deployment domain, e.g.- `tau-twitchname.up.railway.app`. The last two values (`DJANGO_CONFIGURATION` and `PORT`) should use the provided values below.

```
TWITCH_APP_ID=
TWITCH_CLIENT_SECRET=
TWITCH_WEBHOOK_SECRET=
DJANGO_DB_PW=
DJANGO_SECRET_KEY=
PUBLIC_URL=
DJANGO_CONFIGURATION=Railway
PORT=443
```

## Connecting to Websockets

Now that TAU is deployed, you can connect to it via websockets at `wss://tau-twitchname.up.railway.app:443/ws/twitch-events/` using your new deployment domain.
