import os
import requests

from constance import config

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings

from tau.core.utils import log_request

from .models import Streamer, Stream

@receiver(pre_delete, sender=Streamer)
def streamer_deleted(sender, instance, **kwargs):
    if instance.online_subscription is not None:
        headers = {
            'Client-ID': settings.TWITCH_CLIENT_ID,
            'Authorization': f'Bearer {config.TWITCH_APP_ACCESS_TOKEN}',
        }
        sub_id = instance.online_subscription['id']
        req = requests.delete(
            f'https://api.twitch.tv/helix/eventsub/subscriptions?id={sub_id}',
            headers=headers
        )
        if settings.DEBUG_TWITCH_CALLS:
            log_request(req)

    if instance.offline_subscription is not None:
        sub_id = instance.offline_subscription['id']
        req = requests.delete(
            f'https://api.twitch.tv/helix/eventsub/subscriptions?id={sub_id}',
            headers=headers
        )
        if settings.DEBUG_TWITCH_CALLS:
            log_request(req)


@receiver(post_save, sender=Streamer)
def streamer_saved(sender, instance, created, **kwargs):
    if created:
        client_id = settings.TWITCH_CLIENT_ID
        headers = {
            'Authorization': f'Bearer {config.TWITCH_ACCESS_TOKEN}',
            'Client-Id': client_id
        }
        login = instance.twitch_username
        user_r = requests.get(f'https://api.twitch.tv/helix/users?login={login}', headers=headers)
        user_data = user_r.json()
        twitch_id = user_data['data'][0]['id']
        instance.twitch_id = twitch_id
        instance.save()
        instance.init_webhooks()
    else:
        is_streaming = instance.streaming
        if not is_streaming:
            instance.streams.filter(
                ended_at__isnull=True
            ).update(
                ended_at=timezone.now()
            )
        elif not instance.streams.filter(ended_at__isnull=True).exists():
            # create new stream object
            # 1. Fetch stream data from twitch
            client_id = settings.TWITCH_CLIENT_ID
            headers = {
                'Authorization': f'Bearer {config.TWITCH_ACCESS_TOKEN}',
                'Client-Id': client_id
            }
            url = f'https://api.twitch.tv/helix/' \
                f'streams?user_login={instance.twitch_username}'
            data = requests.get(
                url,
                headers=headers
            )
            stream_data = data.json()["data"][0]
            Stream.objects.create(
                stream_id=stream_data['id'],
                streamer=instance,
                game_id=stream_data["game_id"],
                game_name=stream_data['game_name'],
                type=stream_data['type'],
                title=stream_data['title'],
                viewer_count=stream_data['viewer_count'],
                started_at=stream_data['started_at'],
                language=stream_data["language"],
                thumbnail_url=stream_data["thumbnail_url"],
                tag_ids=stream_data["tag_ids"],
                is_mature=stream_data['is_mature']
            )
