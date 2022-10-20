# TAU Local Deployment
The simplest way to deploy TAU is locally, using Docker.  Setting TAU up locally will use `docker-compose` to orchestrate the TAU, Redis, and Postgress containers, and will use ngrok to open a tunnel to your TUA instance for Twitch's webhooks.

1. [Get a Twitch Client ID and Client Secret](./twitch_dev.md)
1. Copy `.env_sample` to `.env`
1. Open and edit the newly created `.env` file. Set the following values.  Please do not use the `#` character in any of your passwords or secret keys.
1. `TWITCH_CLIENT_ID` Set your twitch app client id. This is the "Client ID" available by clicking the "Manage" button for your app on this page: [https://dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps)
1. `TWITCH_CLIENT_SECRET` Set your twitch app secret. This is the "Client Secret" available by clicking the "Manage" button for your  app on this page: [https://dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps) If you don't already one (or you no longer have your  original one), click "New Secret". You'll only be able to see it when you first make it so put it in your password manager.
1. `TWITCH_WEBHOOK_SECRET` This secret is required for Twitch EventSub. It's one that you generate yourself (i.e. it's not the app client secret from the [dev.twitch.tv](https://dev.twitch.tv) page).  The secret must be between 10-100 characters. You can use this one, or genrate one yourself. 
1. `POSTGRES_PW` This is the root password which will be set for your Postgres container. You can use the password set here but it is more secure to set your own strong password. You likely wont need to directly use this password at all.
1. `DJANGO_DB_PW` This is the password used for the django database. You can use the random password already set, but it is more secure to set your own. You likely wont need to  directly use this password at all.
1. `DJANGO_SECRET_KEY` This is a random key for Django. You can use this one, but it's more secure to generate your own.
1. `PORT` The default port is 8000. If you need to use another port, change it here. 
1. `NGROK_TOKEN` It is recommended that you use a free (or paid) ngrok account and token, as non-account tunnels have more limited connection counts.  If you have an ngrok token you would like to use, uncomment the `NGROK_TOKEN` line and provide your token.
1. After saving the .env file, in the root TAU directory execute the command: `docker compose up`
1. Open a web browser and navigate to the url: `http://localhost:PORT/`.
1. Enter in a local TAU username, and password then click "Create Account".  This does not need to be your twitch username.
1. Enter in your Twitch username, and click Setup Channel.
1. Authorize TAU to the requested scopes.

