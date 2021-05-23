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
    def setup_webhooks(public_url, worker_token):
        if config.TWITCH_APP_ACCESS_TOKEN != '':
            print('---- Setting up WebHooks for Twitch ----')
            refresh_access_token()                  # refresh the access token
            print('     [Access tokens refreshed]')
            CoreConfig.teardown_webhooks(public_url, worker_token)          # clear all old webhooks
            print('     [Old WebHooks torn down]')
            CoreConfig.init_webhooks(public_url, worker_token)    # init new webhooks
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
    def init_webhooks(base_url, worker_token):
        from tau.streamers.models import Streamer
        CoreConfig.init_webhook(webhook_payloads.channel_update(base_url), 'STATUS_CHANNEL_UPDATE', base_url, worker_token)
        CoreConfig.init_webhook(webhook_payloads.channel_follow(base_url), 'STATUS_CHANNEL_FOLLOW', base_url, worker_token)
        CoreConfig.init_webhook(
            webhook_payloads.channel_points_redemption(base_url),
            'STATUS_CHANNEL_POINT_REDEMPTION',
            base_url,
            worker_token
        )
        CoreConfig.init_webhook(webhook_payloads.channel_cheer(base_url), 'STATUS_CHANNEL_CHEER', base_url, worker_token)
        CoreConfig.init_webhook(webhook_payloads.channel_raid(base_url), 'STATUS_CHANNEL_RAID', base_url, worker_token)
        CoreConfig.init_webhook(
            webhook_payloads.channel_hype_train_begin(base_url),
            'STATUS_CHANNEL_HYPE_TRAIN_BEGIN',
            base_url,
            worker_token
        )
        CoreConfig.init_webhook(
            webhook_payloads.channel_hype_train_progress(base_url),
            'STATUS_CHANNEL_HYPE_TRAIN_PROGRESS',
            base_url,
            worker_token
        )
        CoreConfig.init_webhook(
            webhook_payloads.channel_hype_train_end(base_url),
            'STATUS_CHANNEL_HYPE_TRAIN_END',
            base_url,
            worker_token
        )
        streamers = Streamer.objects.filter(disabled=False)
        for streamer in streamers:
            CoreConfig.init_webhook(
                webhook_payloads.stream_online(base_url, streamer.twitch_id),
                None,
                base_url,
                worker_token
            )
            CoreConfig.init_webhook(
                webhook_payloads.stream_offline(base_url, streamer.twitch_id),
                None,
                base_url,
                worker_token
            )

    @staticmethod
    def init_webhook(payload, config_key, public_url, worker_token):
        webhook_headers = {
            'Client-ID': os.environ.get('TWITCH_APP_ID', None),
            'Authorization': 'Bearer {}'.format(config.TWITCH_APP_ACCESS_TOKEN),
        }
        if(config_key is not None):
            headers = {'Authorization': f'Token {worker_token}'}
            requests.put(
                f'{public_url}/api/v1/service-status/{config_key}/',
                {'status': 'CONNECTING'},
                headers=headers
            )
        
        requests.post(
            'https://api.twitch.tv/helix/eventsub/subscriptions',
            json=payload,
            headers=webhook_headers
        )
        #TODO Add code to handle bad response from initial sub handshake

    @staticmethod
    def teardown_webhooks(public_url, worker_token):
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

        headers = {'Authorization': f'Token {worker_token}'}

        requests.put(
                f'{public_url}/api/v1/service-status/SET_ALL/',
                {'status': 'DISCONNECTED'},
                headers=headers
            )

