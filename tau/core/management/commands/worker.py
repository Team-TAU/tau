from tau.core.worker import Worker
from tau.core.utils import setup_ngrok
import time
import sys

import requests

from django.conf import settings
from django.core.management.base import BaseCommand

from rest_framework.authtoken.models import Token

from constance import config

from tau.streamers.utils import update_all_streamers   # pylint: disable=import-error
from tau.users.models import User                      # pylint: disable=import-error

class Command(BaseCommand):
    help = 'Connects server to twitch websocket API.'

    def handle(self, *args, **kwargs):
        # try:
        if config.TWITCH_APP_ACCESS_TOKEN == '' or config.CHANNEL_ID == '':
            print("---- Waiting for access token and channel id to be set up. ----")
        
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

        user = User.objects.get(username='worker_process')
        token, created = Token.objects.get_or_create(user=user)
        token = str(token)

        client = Worker(token)
        client.run()
        
        # except:  # pylint: disable=bare-except
        #     e = sys.exc_info()[0]
        #     print(e)
        #     print('---- Exiting ----')
