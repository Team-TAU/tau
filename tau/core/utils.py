import os

import requests

from django.conf import settings

from constance import config

def check_access_token():
    url = "https://id.twitch.tv/oauth2/validate"
    access_token = config.TWITCH_ACCESS_TOKEN
    headers = {"Authorization": f"OAuth {access_token}"}
    req = requests.get(url, headers=headers)
    data = req.json()
    if "status" in data and int(data["status"]) == 401:
        return False
    else:
        return True

def refresh_access_token():
    refresh_token = config.TWITCH_REFRESH_TOKEN
    client_id = os.environ.get('TWITCH_APP_ID', None)
    client_secret = os.environ.get('TWITCH_CLIENT_SECRET', None)
    req = requests.post('https://id.twitch.tv/oauth2/token', data={
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    })
    data = req.json()
    if 'access_token' in data:
        config.TWITCH_REFRESH_TOKEN = data['refresh_token']
        config.TWITCH_ACCESS_TOKEN = data['access_token']
    else:
        print('[ERROR] Could not refresh access token.')

def get_all_statuses():
    keys = [
        'STATUS_WEBSOCKET',
        'STATUS_CHANNEL_UPDATE',
        'STATUS_CHANNEL_FOLLOW',
        'STATUS_CHANNEL_CHEER',
        'STATUS_CHANNEL_POINT_REDEMPTION',
        'STATUS_CHANNEL_RAID',
        'STATUS_CHANNEL_HYPE_TRAIN_BEGIN',
        'STATUS_CHANNEL_HYPE_TRAIN_PROGRESS',
        'STATUS_CHANNEL_HYPE_TRAIN_END',
    ]
    return [
        {'event_type': key, 'old_value': None, 'new_value': getattr(config, key)} for key in keys
    ]

def setup_ngrok():
    # pyngrok will only be installed if it is used.
    from pyngrok import ngrok

    print('---- Setting up ngrok tunnel ----')
    # Get the dev server port (defaults to 8000 for Django, can be overridden with the
    # last arg when calling `runserver`)
    # addrport = urlparse("https://{}".format(sys.argv[-1]))
    # port = addrport.port if addrport.netloc and addrport.port else 8000
    port = int(os.environ.get("PORT", 8000))

    if os.environ.get("USE_NGROK_TOKEN", 'false').lower() == 'true':
        token = os.environ.get("NGROK_TOKEN", None)
        ngrok.set_auth_token(token)

    # Open an ngrok tunnel to the dev server
    public_url = ngrok.connect(port).public_url.replace('http', 'https')
    print(f"     [Tunnel url: {public_url}]\n")

    # Update any base URLs or webhooks to use the public ngrok URL
    settings.BASE_URL = public_url
    return public_url
