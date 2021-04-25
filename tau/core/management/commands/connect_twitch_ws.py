import time

import requests

from django.conf import settings
from django.core.management.base import BaseCommand

from constance import config

from tau.twitchevents.wsclient import WebSocketClient  # pylint: disable=import-error
from tau.core.apps import CoreConfig                   # pylint: disable=import-error
from tau.streamers.utils import update_all_streamers   # pylint: disable=import-error

class Command(BaseCommand):
    help = 'Connects server to twitch websocket API.'

    def handle(self, *args, **kwargs):
        try:
            if config.TWITCH_APP_ACCESS_TOKEN == '' or config.CHANNEL_ID == '':
                print("---- Waitin for access token and channel id to be set up. ----")
            while config.TWITCH_APP_ACCESS_TOKEN == '' or config.CHANNEL_ID == '':
                time.sleep(0.5)

            # Wait for server process to fire up.
            print('---- Waiting for WebHook endpoints to come online ----')
            while 1:
                try:
                    r = requests.get(f'{settings.BASE_URL}/api/v1/heartbeat/')
                    if r.status_code < 500:
                        break
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    pass
                time.sleep(0.5)
            print('     [WebHook endpoints now available]\n')

            # Setup ngrok
            if settings.USE_NGROK:
                public_url = CoreConfig.setup_ngrok()
            else:
                public_url = settings.BASE_URL
            # Setup Webhooks
            print(f'Setting webhooks with base url: {public_url}.')
            CoreConfig.setup_webhooks(public_url)
            # Establish Websocket Connection

            # Update active streamers
            print('---- Updating streaming status of all streamers in DB ----')
            update_all_streamers()
            print('     [Done]\n')

            client = WebSocketClient()
            client.run()
        except:  # pylint: disable=bare-except
            print('---- Exiting ----')
