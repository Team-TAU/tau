import uuid

from django.db import models

class TwitchEvent(models.Model):
    PUBSUB = 'PubSub'
    EVENTSUB = 'EventSub'
    EVENT_SOURCE_CHOICES = [
        (PUBSUB, 'PubSub'),
        (EVENTSUB, 'EventSub')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.CharField(max_length=255, null=True, blank=True)
    event_type = models.CharField(max_length=255)
    event_source = models.CharField(max_length=32, choices=EVENT_SOURCE_CHOICES)
    event_data = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
