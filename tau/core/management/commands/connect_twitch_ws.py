import time
import os

import requests

from django.core.management.base import BaseCommand

from constance import config

from tau.twitchevents.wsclient import WebSocketClient  # pylint: disable=import-error
from tau.core.apps import CoreConfig                   # pylint: disable=import-error

class Command(BaseCommand):
    help = 'Connects server to twitch websocket API.'

    def handle(self, *args, **kwargs):
        try:
            if config.TWITCH_APP_ACCESS_TOKEN == '' or config.CHANNEL_ID == '':
                print("---- Waitin for access token and channel id to be set up. ----")
            while config.TWITCH_APP_ACCESS_TOKEN == '' or config.CHANNEL_ID == '':
                time.sleep(0.5)

            # Wait for server process to fire up.
            print('---- Waiting for WebHooks to come online ----')
            while 1:
                try:
                    port = os.environ.get("TAU_PORT", 8000)
                    r = requests.get(f'http://localhost:{port}/api/v1/heartbeat/')
                    if r.status_code < 500:
                        break
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    pass
                time.sleep(0.5)
            print('     [WebHooks now available]\n')

            # Setup ngrok
            public_url = CoreConfig.setup_ngrok()

            # Setup Webhooks
            CoreConfig.setup_webhooks(public_url)

            # Establish Websocket Connection
            client = WebSocketClient()
            client.run()
        except:  # pylint: disable=bare-except
            print('---- Exiting ----')
