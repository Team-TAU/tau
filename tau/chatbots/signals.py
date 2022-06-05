from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.dispatch import receiver
from .models import ChatBot
from .serializers import ChatBotSerializer


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
