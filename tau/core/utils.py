import os

import requests

from constance import config

def check_access_token():
    url = "https://id.twitch.tv/oauth2/validate"
    access_token = config.TWITCH_ACCESS_TOKEN
    headers = {"Authorization": f"OAuth {access_token}"}
    req = requests.get(url, headers=headers)
    data = req.json()
    if "status" in data and data["status"] == 401:
        return False
    else:
        return True

def refresh_access_token():
    refresh_token = config.TWITCH_REFRESH_TOKEN
    client_id = os.environ.get('TWITCH_APP_ID', None)
    client_secret = os.environ.get('TWITCH_CLIENT_SECRET', None)
    req = requests.post('https://id.twitch.tv/oauth2/token', data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    })
    data = req.json()
    if 'access_token' in data:
        print('Access Token Refreshed.')
        config.TWITCH_REFRESH_TOKEN = data['refresh_token']
        config.TWITCH_ACCESS_TOKEN = data['access_token']
    else:
        print('Could not refresh access token.')

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
        { 'event_type': key, 'old_value': None, 'new_value': getattr(config, key) } for key in keys
    ]
