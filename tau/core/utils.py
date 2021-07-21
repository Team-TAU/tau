import os
import json
from textwrap import indent
import requests

from django.conf import settings

from constance import config

from tau.twitch.models import TwitchEventSubSubscription

def check_access_token():
    url = "https://id.twitch.tv/oauth2/validate"
    access_token = config.TWITCH_ACCESS_TOKEN
    headers = {"Authorization": f"OAuth {access_token}"}
    req = requests.get(url, headers=headers)
    if(settings.DEBUG_TWITCH_CALLS):
        log_request(req)
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
    if(settings.DEBUG_TWITCH_CALLS):
        log_request(req)
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

    token = os.environ.get("NGROK_TOKEN", None)
    if token is not None:
        ngrok.set_auth_token(token)

    # Open an ngrok tunnel to the dev server
    public_url = ngrok.connect(port).public_url.replace('http', 'https')
    print(f"     [Tunnel url: {public_url}]\n")

    # Update any base URLs or webhooks to use the public ngrok URL
    settings.BASE_URL = public_url
    return public_url

def log_request(req):
    print('[REQUEST]')
    print(f'  url: {req.url}')
    print(f'  status: {req.status_code}')
    print(f'  response:')
    if req.text != '':
        print(indent(json.dumps(req.json(), indent=2), '    '))
    else:
        print(f'    NO RESPONSE DATA')

def eventsub_payload(instance, base_url):
    callback_url = f'{base_url}/api/v1/twitch-events/{instance.lookup_name}/webhook/'
    data = {
        "type": instance.name,
        "version": instance.version,
        "condition": {
            "broadcaster_user_id": config.CHANNEL_ID
        },
        "transport": {
            "method": "webhook",
            "callback": callback_url,
            "secret": os.environ.get('TWITCH_WEBHOOK_SECRET', None)
        }
    }
    return data

def init_webhook(payload, url, worker_token):
    webhook_headers = {
        'Client-ID': os.environ.get('TWITCH_APP_ID', None),
        'Authorization': 'Bearer {}'.format(config.TWITCH_APP_ACCESS_TOKEN),
    }
    # if(config_key is not None):
    #     headers = {'Authorization': f'Token {worker_token}'}
    #     req = requests.put(
    #         f'{url}/api/v1/service-status/{config_key}/',
    #         {'status': 'CONNECTING'},
    #         headers=headers
    #     )
    
    req = requests.post(
        'https://api.twitch.tv/helix/eventsub/subscriptions',
        json=payload,
        headers=webhook_headers
    )
    if(settings.DEBUG_TWITCH_CALLS):
        log_request(req)
    #TODO Add code to handle bad response from initial sub handshake

def init_webhooks(base_url, worker_token):
    from tau.streamers.models import Streamer

    url = settings.LOCAL_URL

    for instance in TwitchEventSubSubscription.objects.filter(active=True):
        init_webhook(eventsub_payload(instance, base_url), url, worker_token)

    # streamers = Streamer.objects.filter(disabled=False)
    # for streamer in streamers:
    #     CoreConfig.init_webhook(
    #         webhook_payloads.stream_online(base_url, streamer.twitch_id),
    #         None,
    #         url,
    #         worker_token
    #     )
    #     CoreConfig.init_webhook(
    #         webhook_payloads.stream_offline(base_url, streamer.twitch_id),
    #         None,
    #         url,
    #         worker_token
    #     )

def teardown_webhooks(worker_token):
    url = settings.LOCAL_URL
    
    active_subs = TwitchEventSubSubscription.objects.filter(subscription__isnull=False)

    # Get subscriptions
    headers = {
        'Client-ID': os.environ.get('TWITCH_APP_ID', None),
        'Authorization': 'Bearer {}'.format(config.TWITCH_APP_ACCESS_TOKEN),
    }

    # resp = requests.get('https://api.twitch.tv/helix/eventsub/subscriptions', headers=headers)
    # if(settings.DEBUG_TWITCH_CALLS):
    #     log_request(resp)

    # data = resp.json()
    for sub in active_subs:
        req = requests.delete(
            f'https://api.twitch.tv/helix/eventsub/subscriptions?id={sub.subscription["id"]}',
            headers=headers
        )
        if(settings.DEBUG_TWITCH_CALLS):
            log_request(req)
        sub.status = 'DIS'
        sub.subscription = None
        sub.save()

    # headers = {'Authorization': f'Token {worker_token}'}

    # requests.put(
    #         f'{url}/api/v1/service-status/SET_ALL/',
    #         {'status': 'DISCONNECTED'},
    #         headers=headers
    #     )

