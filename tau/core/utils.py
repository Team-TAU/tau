import os
import json
from textwrap import indent
import requests
import datetime

from django.conf import settings
from django.utils import timezone
from django.apps import apps

from constance import config

from tau.twitch.models import TwitchEventSubSubscription
# from tau.streamers.models import Streamer


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

def check_access_token_expired():
    expiration_time = config.TWITCH_ACCESS_TOKEN_EXPIRATION
    current_time = timezone.now()
    return current_time > expiration_time

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
        expiration = timezone.now() + datetime.timedelta(seconds=data['expires_in'])
        config.TWITCH_ACCESS_TOKEN_EXPIRATION = expiration

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
    ngrok.kill()
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
    tunnel = ngrok.connect(port, bind_tls=True)
    public_url = tunnel.public_url
    print(f"     [Tunnel url: {public_url}]\n")

    # Update any base URLs or webhooks to use the public ngrok URL
    settings.BASE_URL = public_url
    config.PUBLIC_URL = public_url
    return public_url, tunnel

def log_request(req):
    print('[REQUEST]')
    print(f'  url: {req.url}')
    print(f'  status: {req.status_code}')
    print(f'  response:')
    if req.text != '':
        print(indent(json.dumps(req.json(), indent=2), '    '))
    else:
        print(f'    NO RESPONSE DATA')

def eventsub_payload(instance, base_url, broadcaster_key='broadcaster_user_id'):
    callback_url = f'{base_url}/api/v1/twitch-events/{instance.lookup_name}/webhook/'
    data = {
        "type": instance.name,
        "version": instance.version,
        "condition": {
            broadcaster_key: config.CHANNEL_ID
        },
        "transport": {
            "method": "webhook",
            "callback": callback_url,
            "secret": os.environ.get('TWITCH_WEBHOOK_SECRET', None)
        }
    }
    return data
    

def streamer_payload(base_url, status, streamer_id):
    callback_url = f'{base_url}/api/v1/twitch-events/stream-{status}/webhook/'
    data = {
        "type": f'stream.{status}',
        "version": "1",
        "condition": {
            'broadcaster_user_id': streamer_id
        },
        "transport": {
            "method": "webhook",
            "callback": callback_url,
            "secret": os.environ.get('TWITCH_WEBHOOK_SECRET', None)
        }
    }
    return data

def init_webhook(payload, url=None, worker_token=None, instance_id=None):
    webhook_headers = {
        'Client-ID': os.environ.get('TWITCH_APP_ID', None),
        'Authorization': 'Bearer {}'.format(config.TWITCH_APP_ACCESS_TOKEN),
    }
    if(instance_id is not None):
        headers = {'Authorization': f'Token {worker_token}'}
        req = requests.patch(
            f'{url}/api/v1/twitch/eventsub-subscriptions/{instance_id}',
            {'status': 'CTG'},
            headers=headers
        )
    
    req = requests.post(
        'https://api.twitch.tv/helix/eventsub/subscriptions',
        json=payload,
        headers=webhook_headers
    )
    if(settings.DEBUG_TWITCH_CALLS):
        log_request(req)
    #TODO Add code to handle bad response from initial sub handshake

def init_webhooks(base_url, worker_token):
    # from tau.streamers.models import Streamer
    Streamer = apps.get_model('streamers.Streamer')

    url = settings.LOCAL_URL

    active_event_sub_ids = []
    active_streamer_sub_ids = []

    for instance in TwitchEventSubSubscription.objects.filter(active=True):
        if instance.name == 'channel.raid':
            broadcaster_key = 'to_broadcaster_user_id'
        else:
            broadcaster_key = 'broadcaster_user_id'
        init_webhook(
            eventsub_payload(instance, base_url, broadcaster_key),
            url,
            worker_token,
            instance.lookup_name
        )
        active_event_sub_ids.append(instance.id)

    streamers = Streamer.objects.filter(disabled=False)
    for streamer in streamers:
        init_webhook(
           streamer_payload(base_url, 'online', streamer.twitch_id),
            url,
            worker_token
        )
        init_webhook(
            streamer_payload(base_url, 'offline', streamer.twitch_id),
            url,
            worker_token
        )

    return active_event_sub_ids, active_streamer_sub_ids

def get_active_event_sub_ids():
    return [instance.id for instance in TwitchEventSubSubscription.objects.filter(active=True)]

def get_active_streamer_sub_ids():
    Streamer = apps.get_model('streamers.Streamer')
    return [instance.id for instance in Streamer.objects.filter(disabled=False)]

def teardown_webhooks(worker_token):
    Streamer = apps.get_model('streamers.Streamer')
    url = settings.LOCAL_URL
    active_subs = TwitchEventSubSubscription.objects.filter(subscription__isnull=False)
    # Get subscriptions
    headers = {
        'Client-ID': os.environ.get('TWITCH_APP_ID', None),
        'Authorization': 'Bearer {}'.format(config.TWITCH_APP_ACCESS_TOKEN),
    }

    for sub in active_subs:
        req = requests.delete(
            f'https://api.twitch.tv/helix/eventsub/subscriptions?id={sub.subscription["id"]}',
            headers=headers
        )
        if(settings.DEBUG_TWITCH_CALLS):
            log_request(req)
        
        payload = {
            'status': 'DIS',
            'subscription': None
        }
        tau_headers = {'Authorization': f'Token {worker_token}'}
        req = requests.patch(
            f'{url}/api/v1/twitch/eventsub-subscriptions/{sub.lookup_name}',
            json=payload,
            headers=tau_headers
        )
    
    active_streamers_online = Streamer.objects.filter(disabled=False, online_subscription__isnull=False)
    for streamer in active_streamers_online:
        req = requests.delete(
            f'https://api.twitch.tv/helix/eventsub/subscriptions?id={streamer.online_subscription["id"]}',
            headers=headers
        )
        if(settings.DEBUG_TWITCH_CALLS):
            log_request(req)

    active_streamers_offline = Streamer.objects.filter(disabled=False, offline_subscription__isnull=False)
    for streamer in active_streamers_offline:
        req = requests.delete(
            f'https://api.twitch.tv/helix/eventsub/subscriptions?id={streamer.offline_subscription["id"]}',
            headers=headers
        )
        if(settings.DEBUG_TWITCH_CALLS):
            log_request(req)


def teardown_all_acct_webhooks():
    headers = {
        'Client-ID': os.environ.get('TWITCH_APP_ID', None),
        'Authorization': 'Bearer {}'.format(config.TWITCH_APP_ACCESS_TOKEN),
    }

    resp = requests.get('https://api.twitch.tv/helix/eventsub/subscriptions', headers=headers)

    if(settings.DEBUG_TWITCH_CALLS):
        log_request(resp)
    
    data = resp.json()

    for row in data['data']:
        req = requests.delete(
            'https://api.twitch.tv/helix/eventsub/subscriptions?id={}'.format(row['id']),
            headers=headers
        )
        if(settings.DEBUG_TWITCH_CALLS):
            log_request(resp)
