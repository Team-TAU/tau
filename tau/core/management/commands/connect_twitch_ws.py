import time

from django.core.management.base import BaseCommand, CommandError

from constance import config

from tau.twitchevents.wsclient import WebSocketClient
from tau.core.apps import CoreConfig

class Command(BaseCommand):
    help = 'Connects server to twitch websocket API.'

    def handle(self, *args, **kwargs):
        try:
            if config.TWITCH_APP_ACCESS_TOKEN == '' or config.CHANNEL_ID == '':
                print("---- Waiting for access token and channel id to be set up. ----")
            while config.TWITCH_APP_ACCESS_TOKEN == '' or config.CHANNEL_ID == '':
                time.sleep(0.5)

            # Setup ngrok
            public_url = CoreConfig.setup_ngrok()
            # Setup Webhooks
            CoreConfig.setup_webhooks(public_url)

            # Establish Websocket Connection
            client = WebSocketClient()
            client.run()
        except:
            raise CommandError("There was an error.")
