import os
import requests

from constance import config

from .models import Streamer

def update_all_streamers():
    #TODO- Update to handle more than 100 streamers in db

    #TODO- I am currently calling the twitch API 2x for each active streamer.Streamer
    #      refeactor to use returned stream data.

    streamers = Streamer.objects.all()
    streamer_ids = [streamer.twitch_id for streamer in streamers]
    streamer_ids_param = '&'.join([f'user_id={id}' for id in streamer_ids])

    client_id = os.environ.get('TWITCH_APP_ID', None)
    headers = {
        'Authorization': 'Bearer {}'.format(config.TWITCH_ACCESS_TOKEN),
        'Client-Id': client_id
    }
    url = f'https://api.twitch.tv/helix/' \
          f'streams?first=100&{streamer_ids_param}'
    data = requests.get(
        url,
        headers=headers
    )
    stream_data = data.json()["data"]
    active_streamer_ids = [row['user_id'] for row in stream_data]

    for streamer in streamers:
        streamer.streaming = streamer.twitch_id in active_streamer_ids
        streamer.save()
