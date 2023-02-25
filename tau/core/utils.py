import os
import json
import datetime

from textwrap import indent
import requests

from django.conf import settings
from django.utils import timezone
from django.apps import apps

from constance import config
from tau.chatbots.models import ChatBot

from tau.twitch.models import TwitchEventSubSubscription
# from tau.streamers.models import Streamer


def check_access_token():
    url = "https://id.twitch.tv/oauth2/validate"
    access_token = config.TWITCH_ACCESS_TOKEN
    headers = {"Authorization": f"OAuth {access_token}"}
    req = requests.get(url, headers=headers)
    if settings.DEBUG_TWITCH_CALLS:
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
    client_id = settings.TWITCH_CLIENT_ID
    client_secret = os.environ.get('TWITCH_CLIENT_SECRET', None)
    req = requests.post('https://id.twitch.tv/oauth2/token', data={
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    })
    if settings.DEBUG_TWITCH_CALLS:
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
    print('  response:')
    if req.text != '':
        print(indent(json.dumps(req.json(), indent=2), '    '))
    else:
        print('    NO RESPONSE DATA')

def eventsub_payload(instance, base_url, condition=None):
    callback_url = f'{base_url}/api/v1/twitch-events/{instance.lookup_name}/webhook/'
    if condition is None:
        condition = {"broadcaster_user_id": config.CHANNEL_ID}
    data = {
        "type": instance.name,
        "version": instance.version,
        "condition": condition,
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
        'Client-ID': settings.TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {config.TWITCH_APP_ACCESS_TOKEN}',
    }
    if instance_id is not None:
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
    if settings.DEBUG_TWITCH_CALLS:
        log_request(req)
    # TODO Add code to handle bad response from initial sub handshake

def get_conditions(instance):
    if instance.name == 'channel.raid':
        return [
            {'to_broadcaster_user_id': config.CHANNEL_ID},
            {'from_broadcaster_user_id': config.CHANNEL_ID}
        ]
    else:
        return [{
            key: config.CHANNEL_ID for key in instance.condition_schema['required']
        }]

def init_webhooks(base_url, worker_token):
    # from tau.streamers.models import Streamer
    Streamer = apps.get_model('streamers.Streamer')

    url = settings.LOCAL_URL

    active_event_sub_ids = []
    active_streamer_sub_ids = []

    for instance in TwitchEventSubSubscription.objects.filter(active=True):
        conditions = get_conditions(instance)
        for properties in conditions:
            init_webhook(
                eventsub_payload(instance, base_url, properties),
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
        'Client-ID': settings.TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {config.TWITCH_APP_ACCESS_TOKEN}',
    }

    for sub in active_subs:
        if isinstance(sub.subscription, list):
            for sub_dat in sub.subscription:
                req = requests.delete(
                    f'https://api.twitch.tv/helix/eventsub/subscriptions?id={sub_dat["id"]}',
                    headers=headers
                )
                if settings.DEBUG_TWITCH_CALLS:
                    log_request(req)
        else:
            req = requests.delete(
                f'https://api.twitch.tv/helix/eventsub/subscriptions?id={sub.subscription["id"]}',
                headers=headers
            )
            if settings.DEBUG_TWITCH_CALLS:
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

    active_streamers_online = Streamer.objects.filter(
        disabled=False, online_subscription__isnull=False
    )
    for streamer in active_streamers_online:
        sub_id = streamer.online_subscription["id"]
        req = requests.delete(
            f'https://api.twitch.tv/helix/eventsub/subscriptions?id={sub_id}',
            headers=headers
        )
        if settings.DEBUG_TWITCH_CALLS:
            log_request(req)

    active_streamers_offline = Streamer.objects.filter(
        disabled=False, offline_subscription__isnull=False
    )
    for streamer in active_streamers_offline:
        sub_id = streamer.offline_subscription["id"]
        req = requests.delete(
            f'https://api.twitch.tv/helix/eventsub/subscriptions?id={sub_id}',
            headers=headers
        )
        if settings.DEBUG_TWITCH_CALLS:
            log_request(req)

def cleanup_webhooks():
    headers = {
        'Client-ID': settings.TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {config.TWITCH_APP_ACCESS_TOKEN}',
    }

    resp = requests.get('https://api.twitch.tv/helix/eventsub/subscriptions', headers=headers)

    if settings.DEBUG_TWITCH_CALLS:
        log_request(resp)

    data = resp.json()

    bad_webhooks = list(filter(lambda x: (x['status'] != 'enabled'), data['data']))

    for webhook in bad_webhooks:
        req = requests.delete(
            f'https://api.twitch.tv/helix/eventsub/subscriptions?id={webhook["id"]}',
            headers=headers
        )
        if settings.DEBUG_TWITCH_CALLS:
            log_request(req)


def cleanup_remote_webhooks():
    headers = {
        'Client-ID': settings.TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {config.TWITCH_APP_ACCESS_TOKEN}',
    }

    resp = requests.get('https://api.twitch.tv/helix/eventsub/subscriptions', headers=headers)

    if settings.DEBUG_TWITCH_CALLS:
        log_request(resp)

    data = resp.json()

    public_url = config.PUBLIC_URL.split('/')[2]

    remote_webhooks = list(
        filter(lambda x: (x["transport"]["callback"].split("/")[2] != public_url), data['data']))

    for row in remote_webhooks:
        req = requests.delete(
            f'https://api.twitch.tv/helix/eventsub/subscriptions?id={row["id"]}',
            headers=headers
        )
        if settings.DEBUG_TWITCH_CALLS:
            log_request(req)

def teardown_all_acct_webhooks():
    headers = {
        'Client-ID': settings.TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {config.TWITCH_APP_ACCESS_TOKEN}',
    }

    resp = requests.get('https://api.twitch.tv/helix/eventsub/subscriptions', headers=headers)

    if settings.DEBUG_TWITCH_CALLS:
        log_request(resp)

    data = resp.json()

    for row in data['data']:
        req = requests.delete(
            f'https://api.twitch.tv/helix/eventsub/subscriptions?id={row["id"]}',
            headers=headers
        )
        if settings.DEBUG_TWITCH_CALLS:
            log_request(req)

def handle_tau_bot_token(bot_id, response_data):
    access_token = response_data['access_token']
    refresh_token = response_data['refresh_token']
    expiration = timezone.now() + datetime.timedelta(seconds=response_data['expires_in'])
    bot = ChatBot.objects.get(pk=bot_id)
    bot.access_token = access_token
    bot.refresh_token = refresh_token
    bot.token_expiration = expiration
    bot.save()

def handle_tau_streamer_token(response_data, client_id, client_secret):
    config.TWITCH_ACCESS_TOKEN = response_data['access_token']
    config.TWITCH_REFRESH_TOKEN = response_data['refresh_token']
    expiration = timezone.now() + datetime.timedelta(seconds=response_data['expires_in'])
    config.TWITCH_ACCESS_TOKEN_EXPIRATION = expiration
    scope = ' '.join(settings.TOKEN_SCOPES)
    app_auth_r = requests.post('https://id.twitch.tv/oauth2/token', data={
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': scope
    })
    if settings.DEBUG_TWITCH_CALLS:
        log_request(app_auth_r)
    app_auth_data = app_auth_r.json()
    config.TWITCH_APP_ACCESS_TOKEN = app_auth_data['access_token']
    config.SCOPE_UPDATED_NEEDED = False
    config.SCOPES_REFRESHED = True
    headers = {
        'Authorization': f'Bearer {config.TWITCH_ACCESS_TOKEN}',
        'Client-Id': client_id
    }
    user_r = requests.get('https://api.twitch.tv/helix/users', headers=headers)
    if settings.DEBUG_TWITCH_CALLS:
        log_request(user_r)
    user_data = user_r.json()
    channel_id = user_data['data'][0]['id']
    config.CHANNEL_ID = channel_id

def parse_message(data):
    message = {
        'raw': data,
        'tags': {},
        'prefix': None,
        'command': None,
        'params': [],
        'message-text': None
    }

    position = 0
    nextspace = 0

    if data[0] == '@':
        nextspace = data.find(' ')
        if nextspace == -1:
            return None

        raw_tags = data[1:nextspace].split(';')
        for tag in raw_tags:
            pair = tag.split('=')
            if len(pair) == 1:
                value = True
            else:
                value = pair[1]
            message['tags'][pair[0]] = value
        position = nextspace + 1

        while data[position] == ' ':
            position += 1

    if data[position] == ':':
        nextspace = data.find(' ', position)

        if nextspace == -1:
            return None

        message['prefix'] = data[position:nextspace]

        position = nextspace + 1

        while data[position] == ' ':
            position += 1

    nextspace = data.find(' ', position)

    if nextspace == -1:
        if len(data) > position:
            message['command'] = data[position:]
        else:
            message['command'] = None
        return message

    message['command'] = data[position:nextspace]

    while data[position] == ' ':
        position += 1

    while position < len(data):
        nextspace = data.find(' ', position)
        if data[position] == ':':
            message['params'].append(data[position:])
            break

        if nextspace != -1:
            message['params'].append(data[position:nextspace])
            position = nextspace + 1

            while data[position] == ' ':
                position += 1

            continue

        if nextspace == -1:
            message['params'].append(data[position:])
            break

    if message['command'] == 'PRIVMSG':
        message['message-text'] = message['params'][2][1:].replace("\n", "").replace("\r", "")

    if 'emotes' in message['tags']:
        emotes = message['tags']['emotes']
        emote_list = []
        if emotes != '':
            for emote_txt in emotes.split('/'):
                emote_data = emote_txt.split(':')
                emote_list.append({
                    'id': emote_data[0],
                    'positions': [
                        [int(val) for val in position.split('-')]
                        for position in emote_data[1].split(',')
                    ]
                })
        message['tags']['emotes'] = emote_list

    return message

def lookup_setting(setting):
    return getattr(config, setting)
