# Railway Deployment

[Railway](https://railway.app/) is a cost effective way to run TAU 24/7 in the cloud. The following steps should get you started! These instructions assume you have cloned the TAU repo to your local drive, and that you have npm installed (the railway CLI app requires npm).

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2FTeam-TAU%2Ftau&plugins=postgresql%2Credis&envs=TWITCH_APP_ID%2CTWITCH_CLIENT_SECRET%2CTWITCH_WEBHOOK_SECRET%2CDJANGO_DB_PW%2CDJANGO_SECRET_KEY%2CPUBLIC_URL%2CDJANGO_CONFIGURATION%2CDJANGO_DB_HOST%2CDJANGO_DB_PORT%2CDJANGO_DB_TYPE%2CPORT%2CPOSTGRES_PASSWORD%2CPROTOCOL%2CREDIS_ENDPOINT&TWITCH_APP_IDDesc=Your+Twitch+Application%2FClient+ID&TWITCH_CLIENT_SECRETDesc=Your+Twitch+Client+Secret&TWITCH_WEBHOOK_SECRETDesc=A+random+string+of+10-100+characters&DJANGO_DB_PWDesc=Password+of+your+choice+for+the+django+database&DJANGO_SECRET_KEYDesc=A+random+string+of+10-100+characters&PUBLIC_URLDesc=Your+railway+deployment+url+%28e.g.-+tau-twitchname.up.railway.app%29&DJANGO_CONFIGURATIONDesc=Django+config+type+%28for+security%2C+leave+as+Production%29&DJANGO_DB_HOSTDesc=To+use+railway+postgres%2C+do+not+change.&DJANGO_DB_PORTDesc=To+use+railway+postgres%2C+do+not+change.&DJANGO_DB_TYPEDesc=To+use+railway+postgres%2C+do+not+change.&PORTDesc=Do+not+change&POSTGRES_PASSWORDDesc=To+use+railway+postgres%2C+do+not+change.&PROTOCOLDesc=Do+not+change&REDIS_ENDPOINTDesc=To+use+railway+redis%2C+do+not+change.&DJANGO_CONFIGURATIONDefault=Production&DJANGO_DB_HOSTDefault=%24%7B%7B+PGHOST+%7D%7D&DJANGO_DB_PORTDefault=%24%7B%7B+PGPORT+%7D%7D&DJANGO_DB_TYPEDefault=postgres&PORTDefault=443&POSTGRES_PASSWORDDefault=%24%7B%7B+PGPASSWORD+%7D%7D&PROTOCOLDefault=https%3A&REDIS_ENDPOINTDefault=%24%7B%7B+REDISUSER+%7D%7D%3A%24%7B%7B+REDISPASSWORD+%7D%7D%40%24%7B%7B+REDISHOST+%7D%7D%3A%24%7B%7B+REDISPORT+%7D%7D&referralCode=TAU)

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
