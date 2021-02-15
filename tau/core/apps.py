import sys
import os
from urllib.parse import urlparse

import requests

from django.apps import AppConfig
from django.conf import settings

from constance import config

import tau.twitchevents.webhook_payloads as webhook_payloads
from .utils import refresh_access_token

class CoreConfig(AppConfig):
    name = 'tau.core'
    verbose_name = 'Core'

    @staticmethod
    def setup_webhooks(public_url):
        if config.TWITCH_APP_ACCESS_TOKEN != '':
            refresh_access_token()                  # refresh the access token
            CoreConfig.teardown_webhooks()          # clear all old webhooks
            CoreConfig.init_webhooks(public_url)    # init new webhooks
        else:
            print(
                'You have not yet set up a username, or authorized Tau to connect ' \
                'to your twitch account.  Webhooks will be set up after you do so.'
            )

    @staticmethod
    def setup_ngrok():
        # pyngrok will only be installed if it is used.
        from pyngrok import ngrok

        # Get the dev server port (defaults to 8000 for Django, can be overridden with the
        # last arg when calling `runserver`)
        addrport = urlparse("https://{}".format(sys.argv[-1]))
        port = addrport.port if addrport.netloc and addrport.port else 8000

        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(port).public_url.replace('http', 'https')
        print("ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

        # Update any base URLs or webhooks to use the public ngrok URL
        settings.BASE_URL = public_url
        return public_url

    @staticmethod
    def init_webhooks(base_url):
        CoreConfig.init_webhook(webhook_payloads.channel_update(base_url), 'STATUS_CHANNEL_UPDATE')
        CoreConfig.init_webhook(webhook_payloads.channel_follow(base_url), 'STATUS_CHANNEL_FOLLOW')
        CoreConfig.init_webhook(
            webhook_payloads.channel_points_redemption(base_url),
            'STATUS_CHANNEL_POINT_REDEMPTION'
        )
        CoreConfig.init_webhook(webhook_payloads.channel_cheer(base_url), 'STATUS_CHANNEL_CHEER')
        CoreConfig.init_webhook(webhook_payloads.channel_raid(base_url), 'STATUS_CHANNEL_RAID')
        CoreConfig.init_webhook(
            webhook_payloads.channel_hype_train_begin(base_url),
            'STATUS_CHANNEL_HYPE_TRAIN_BEGIN'
        )
        CoreConfig.init_webhook(
            webhook_payloads.channel_hype_train_progress(base_url),
            'STATUS_CHANNEL_HYPE_TRAIN_PROGRESS'
        )
        CoreConfig.init_webhook(
            webhook_payloads.channel_hype_train_end(base_url),
            'STATUS_CHANNEL_HYPE_TRAIN_END'
        )

    @staticmethod
    def init_webhook(payload, config_key):
        webhook_headers = {
            'Client-ID': os.environ.get('TWITCH_APP_ID', None),
            'Authorization': 'Bearer {}'.format(config.TWITCH_APP_ACCESS_TOKEN),
        }
        setattr(config, config_key, 'CONNECTING')
        requests.post(
            'https://api.twitch.tv/helix/eventsub/subscriptions',
            json=payload,
            headers=webhook_headers
        )
        # TODO Add code to handle bad response from initial sub handshake

    @staticmethod
    def teardown_webhooks():
        # Get subscriptions
        headers = {
            'Client-ID': os.environ.get('TWITCH_APP_ID', None),
            'Authorization': 'Bearer {}'.format(config.TWITCH_APP_ACCESS_TOKEN),
        }

        resp = requests.get('https://api.twitch.tv/helix/eventsub/subscriptions', headers=headers)

        data = resp.json()
        for row in data['data']:
            requests.delete(
                'https://api.twitch.tv/helix/eventsub/subscriptions?id={}'.format(row['id']),
                headers=headers
            )
        config.STATUS_CHANNEL_UPDATE = 'DISCONNECTED'
        config.STATUS_CHANNEL_FOLLOW = 'DISCONNECTED'
        config.STATUS_CHANNEL_CHEER = 'DISCONNECTED'
        config.STATUS_CHANNEL_POINT_REDEMPTION = 'DISCONNECTED'
        config.STATUS_CHANNEL_RAID = 'DISCONNECTED'
        config.STATUS_CHANNEL_HYPE_TRAIN_BEGIN = 'DISCONNECTED'
        config.STATUS_CHANNEL_HYPE_TRAIN_PROGRESS = 'DISCONNECTED'
        config.STATUS_CHANNEL_HYPE_TRAIN_END = 'DISCONNECTED'
