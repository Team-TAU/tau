

# Send message over twitchevents ws whenever a twitch-event is updated
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from asgiref.sync import async_to_sync

from .models import TwitchEventSubSubscription
from .serializers import TwitchEventSubSubscriptionSerializer


@receiver(post_save, sender=TwitchEventSubSubscription)
def twitch_event_saved(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    serializer = TwitchEventSubSubscriptionSerializer(instance=instance)
    data = serializer.data
    async_to_sync(channel_layer.group_send)('taustatus', {
      'type': 'taustatus.event',
      'data': data
    })
