from django.db.models.signals import post_save
from django.dispatch import receiver

from constance import config
from constance.signals import config_updated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import TwitchEvent
from .serializers import TwitchEventSerializer

# Send message over twitchevents ws whenever a twitch-event is updated
@receiver(post_save, sender=TwitchEvent)
def twitch_event_saved(sender, instance, created, **kwargs):
    if config.USE_IRC and created and instance.event_type == 'channel-channel_points_custom_reward_redemption-add' and instance.event_data['user_input'] != '':
        return
    print('broadcasting twitch event')
    channel_layer = get_channel_layer()
    serializer = TwitchEventSerializer(instance=instance)
    data = serializer.data
    async_to_sync(channel_layer.group_send)('twitchevents', {
        'type': 'twitchevent.event',
        'data': data
    })

# Send message over taustatus ws whenever a constance value is updated
@receiver(config_updated)
def constance_updated(sender, key, old_value, new_value, **kwargs):
    if key.startswith('STATUS'):
        payload = [{
            'event_type': key,
            'old_value': old_value,
            'new_value': new_value
        }]
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('taustatus', {
            'type': 'taustatus.event',
            'data': payload
        })
