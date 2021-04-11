import os

import requests

from django.apps import AppConfig

from constance import config

import tau.twitchevents.webhook_payloads as webhook_payloads
from .utils import refresh_access_token, setup_ngrok


class CoreConfig(AppConfig):
    name = 'tau.core'
    verbose_name = 'Core'

    @staticmethod
    def setup_webhooks(public_url):
        if config.TWITCH_APP_ACCESS_TOKEN != '':
            print('---- Setting up WebHooks for Twitch ----')
            refresh_access_token()                  # refresh the access token
            print('     [Access tokens refreshed]')
            CoreConfig.teardown_webhooks()          # clear all old webhooks
            print('     [Old WebHooks torn down]')
            CoreConfig.init_webhooks(public_url)    # init new webhooks
            print('     [New WebHooks Initialized]\n')
        else:
            print(
                'You have not yet set up a username, or authorized Tau to connect '
                'to your twitch account.  Webhooks will be set up after you do so.'
            )

    @staticmethod
    def setup_ngrok():
        return setup_ngrok()

    @staticmethod
    def init_webhooks(base_url):
        from tau.streamers.models import Streamer
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
        streamers = Streamer.objects.filter(disabled=False)
        for streamer in streamers:
            CoreConfig.init_webhook(
                webhook_payloads.stream_online(base_url, streamer.twitch_id),
                None
            )
            CoreConfig.init_webhook(
                webhook_payloads.stream_offline(base_url, streamer.twitch_id),
                None
            )

    @staticmethod
    def init_webhook(payload, config_key):
        webhook_headers = {
            'Client-ID': os.environ.get('TWITCH_APP_ID', None),
            'Authorization': 'Bearer {}'.format(config.TWITCH_APP_ACCESS_TOKEN),
        }
        if(config_key is not None):
            setattr(config, config_key, 'CONNECTING')
        
        requests.post(
            'https://api.twitch.tv/helix/eventsub/subscriptions',
            json=payload,
            headers=webhook_headers
        )
        #TODO Add code to handle bad response from initial sub handshake

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
