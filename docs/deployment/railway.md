# Railway Deployment

[Railway](https://railway.app/) is a cost effective way to run TAU 24/7 in the cloud. The following steps should get you started! These instructions assume you have cloned the TAU repo to your local drive, and that you have npm installed (the railway CLI app requires npm).

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2FTeam-TAU%2Ftau%2Ftree%2Fdocumentation-railway-docs&plugins=postgresql%2Credis&envs=TWITCH_APP_ID%2CTWITCH_CLIENT_SECRET%2CTWITCH_WEBHOOK_SECRET%2CDJANGO_DB_PW%2CDJANGO_SECRET_KEY%2CDJANGO_CONFIGURATION%2CPORT&TWITCH_APP_IDDesc=Your+Twitch+TAU+app+id.&TWITCH_CLIENT_SECRETDesc=Your+Twitch+TAU+client+secret.&TWITCH_WEBHOOK_SECRETDesc=Random+string+of+10-100+characters.&DJANGO_DB_PWDesc=A+password+you+would+like+to+use+for+your+TAU+postgres+database.&DJANGO_SECRET_KEYDesc=Random+string+of+10-100+characters.&DJANGO_CONFIGURATIONDesc=DO+NOT+CHANGE&PORTDesc=DO+NOT+CHANGE&DJANGO_CONFIGURATIONDefault=Railway&PORTDefault=443&referralCode=TAU)

1. [Create a railway account/login](https://railway.app/login)
1. [Go to your railway dashboard](https://railway.app/dashboard)
1. Click "+ New Project" and select "Empty Project"
1. Click "Add Plugin" and select "Add PostgreSQL"
1. Click "Add Plugin" and select "Add Redis"
1. Click "Deployments" then the "Domains" tab. Edit the production domain to a url that you want (e.g.- tau-twitchname.up.railway.com). Note this domain, as it will be required in your environment variables, and when setting up TAU in the twitch dev dashboard.
1. Click "Variables", then on "Custom". Create a new variable with the name `TAU`, and the value `True`. This is required (for some reason?) to add the environment variable `bulk edit` option which you should now see under the variable add section. You will use `bulk edit` in a couple of steps.
1. [Get a Twitch Client ID and Client Secret](./twitch_dev.md). NOTE- rather than `http://localhost:PORT/twitch-callback/` as your OAuth redirect URL, you must use https, the domain you set up in the prior step, and no port. E.g.: `https://tau-twitchname.up.railway.com`.
1. Copy the sample `.env` data below, and paste in a text editor. Add values for the first six enviornment variables as explained below.
1. Back in the `Variables` section of your railway project, click `Bulk Import`, and paste in your edited .env data, and click `Add`. If desired, you can now delete the `TAU` variable you created before (leaving it wont hurt anything).
1. In a terminal install the railway CLI using npm: `npm i -g @railway/cli` then login to railway: `railway login`
1. In your railway project dashboard, click on "Setup". Copy the link command with your projects UUID (something like: `railway link SOME-UUID-HERE`)
1. In the terminal, navigate to the TAU root directory, and paste/run the link command.
1. In the terminal, spin up your railway TAU instance (from the root TAU directory) with the command: `railway up`.
1. After the container spins up, navigate to your projects url, and complete the setup wizard.
1. You're now running TAU!

## Sample .env data.

The first 6 values must be set. `TWITCH_CLIENT_SECRET` and `TWITCH_APP_ID` come from the Twitch developer settings above, `TWITCH_WEBHOOK_SECRET` should be a random string of characters 10-100 characters long. `DJANGO_SECRET_KEY` should be a different random string of characters 10-100 characters long, `DJANGO_DB_PW` can be any password you want to set for the Django databse user, and `PUBLIC_URL` should be the deployment domain, e.g.- `tau-twitchname.up.railway.com`.

```
TWITCH_CLIENT_SECRET=
TWITCH_APP_ID=
TWITCH_WEBHOOK_SECRET=
DJANGO_SECRET_KEY=
DJANGO_DB_PW=
PUBLIC_URL=
DJANGO_DB_TYPE=postgres
DJANGO_DB_HOST=${{ PGHOST }}
DJANGO_DB_PORT=${{ PGPORT }}
DJANGO_DB_USER=tau
DJANGO_DB=tau
REDIS_ENDPOINT=${{ REDISUSER }}:${{ REDISPASSWORD }}@${{ REDISHOST }}:${{ REDISPORT }}
DJANGO_CONFIGURATION=Local
PORT=443
PROTOCOL=https:
POSTGRES_PASSWORD=${{ PGPASSWORD }}
DEBUG_TWITCH_CALLS=False
USE_NGROK=False
```
