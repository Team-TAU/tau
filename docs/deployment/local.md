# TAU Local Deployment
Paragraph that says what we're doing..
1. [Get a Twitch Client ID and Client Secret](./twitch_dev.md)
1. Copy .env_sample to .env
1. Open and edit the newly created .env file.  Follow the directions below.
```
##########################################################
# Set your twitch app client id. This is the "Client ID" 
# available by clicking the "Manage" button for your 
# app on this page:
# https://dev.twitch.tv/console/apps

TWITCH_APP_ID=


##########################################################
# Set your twitch app secret. This is the "Client Secret"
# available by clicking the "Manage" button for your 
# app on this page:
# https://dev.twitch.tv/console/apps
# If you don't already one (or you no longer have your 
# original one), click "New Secret". You'll only be able
# to see it when you first make it so put it in your
# password manager

TWITCH_CLIENT_SECRET=


##########################################################
# This secret is required for Twitch EventSub. It's 
# one that you generate yourself (i.e. it's not the
# app client secret from the dev.twitch.tv page).  
# The secret must be between 10-100 characters. You 
# can use this one, or genrate one yourself. 

TWITCH_WEBHOOK_SECRET=xvsYjbtbqeL4DVgT8vXV


##########################################################
# This is the root password which will be set for your
# Postgres container. You can use the password set here
# but it is more secure to set your own strong password.
# You likely wont need to directly use this password at
# all.

POSTGRES_PW=7Rt879up6s3bT2UqeHMv


##########################################################
# This is the password used for the django database. You
# can use the random password already set, but it is more
# secure to set your own. You likely wont need to 
# directly use this password at all.

DJANGO_DB_PW=f7UXs2mAZSnpX492H4m5


##########################################################
# This is a random key for Django. You can use this 
# one, but it's more secure to generate your own.

DJANGO_SECRET_KEY=F9MvDGErwTE7kLuxB7sq


##########################################################
# The default port is 8000. If you need to use 
# another port, change it here. 

PORT=8000


##########################################################
# It is recommended that you use a free (or paid) ngrok 
# account and token, as non-account tunnels have more
# limited connection counts.  If you have an ngrok
# token you would like to use, uncomment the line below
# and provide your token.

# NGROK_TOKEN=

```
4. After saving the .env file, in the root TAU directory execute the command: `docker compose up`
4. Open a web browser and navigate to the url: `http://localhost:PORT/`.
4. Enter in a local TAU username, and password then click "Create Account".  This does not need to be your twitch username.
4. Enter in your Twitch username, and click Setup Channel.
4. Authorize TAU to the requested scopes.
