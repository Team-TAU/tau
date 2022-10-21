from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import ChatBot, ChatBotChannel
from .serializers import ChatBotSerializer


@receiver(post_save, sender=ChatBotChannel)
def chat_bot_channel_saved(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('serverworker', {
            'type': 'serverworker_event',
            'data': {
                'action': 'add-bot-channel',
                'bot': str(instance.chat_bot.user_login),
                'channel': instance.channel
            }
        })

@receiver(pre_delete, sender=ChatBotChannel)
def chat_bot_channel_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('serverworker', {
        'type': 'serverworker_event',
        'data': {
            'action': 'remove-bot-channel',
            'bot': str(instance.chat_bot.user_login),
            'channel': instance.channel
        }
    })

@receiver(post_save, sender=ChatBot)
def chat_bot_saved(sender, instance, created, **kwargs):
    if created:
        event = 'Created'
    else:
        event = 'Updated'
    channel_layer = get_channel_layer()
    serializer = ChatBotSerializer(instance=instance)
    data = serializer.data
    async_to_sync(channel_layer.group_send)('chatbotstatus', {
        'type': 'chatbotstatus.event',
        'data': {'event': event, 'chatBot': data}
    })
    if created:
        async_to_sync(channel_layer.group_send)('serverworker', {
            'type': 'serverworker_event',
            'data': {'action': 'add-bot', 'bot_id': str(instance.id)}
        })
