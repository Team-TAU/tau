# Twitch Setup

Because TAU depends heavily on Twitch, it is necessary to obtain a Twitch App ID and
secret. The steps below will help you do this.

1. Determine the port you want to run TAU on.  By default this is port 8000.  Use this value for `PORT` in the following steps.
1. Visit the [Twitch Developer Applications Console](https://dev.twitch.tv/console/apps).
1. Log in to your Twitch account if you are not already logged in.
1. In order to manage applications, you will need to enable 2FA for your account.
1. Click "+ Register Your Application".
1. Fill in a name for TAU. I recommend TAU- YourTwitchName.
1. Add `http://localhost:PORT/twitch-callback/` as an OAuth Redirect URL. (Note the trailing slash, this is required)
1. Select a category for what you'll be using TAU for. Chat Bot is what I've used.
1. Click "Create"
1. Click "Manage" for the TAU app.
1. Here is where you can find your Client ID, and generate a Client Secret. You'll need these two values later. Note- you can only see the client secret when you generate it, so make sure you copy it to put in your .env file later. Dont worry if you lose it, you can always generate a new secret.
