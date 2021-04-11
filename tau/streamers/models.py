import uuid

from django.db import models

# Create your models here.
class Streamer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    twitch_username = models.CharField(max_length=64)
    twitch_id = models.CharField(max_length=64, null=True, blank=True)
    streaming = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
