import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from rest_framework.authtoken.models import Token

from constance import config

from tau.twitchevents.ircclient import IRCClient
from tau.users.models import User

class Command(BaseCommand):
    help = 'Connects server to twitch websocket API.'

    def handle(self, *args, **kwargs):
        try:
            if config.TWITCH_APP_ACCESS_TOKEN == '' or config.CHANNEL_ID == '':
                print("---- Waitin for access token and channel id to be set up. ----")
            while config.TWITCH_APP_ACCESS_TOKEN == '' or config.CHANNEL_ID == '':
                time.sleep(0.5)
            
            user = User.objects.get(username='worker_process')
            token, created = Token.objects.get_or_create(user=user)
            token = str(token)
            client = IRCClient(token=token)
            client.run()
        except:  # pylint: disable=bare-except
            e = sys.exc_info()[0]
            print(e)
            print('---- Exiting ----')
