import os
import requests

from constance import config

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Streamer

@receiver(post_save, sender=Streamer)
def streamer_saved(sender, instance, created, **kwargs):
    if created:
        client_id = os.environ.get('TWITCH_APP_ID', None)
        headers = {
            'Authorization': 'Bearer {}'.format(config.TWITCH_ACCESS_TOKEN),
            'Client-Id': client_id
        }
        login = instance.twitch_username
        user_r = requests.get(f'https://api.twitch.tv/helix/users?login={login}', headers=headers)
        user_data = user_r.json()
        twitch_id = user_data['data'][0]['id']
        instance.twitch_id = twitch_id
        instance.save()
    