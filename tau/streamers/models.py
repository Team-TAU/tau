import uuid

from django.db import models

# Create your models here.
class Streamer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    twitch_username = models.CharField(max_length=64, unique=True)
    twitch_id = models.CharField(max_length=64, null=True, blank=True, unique=True)
    streaming = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    subscription = models.JSONField(blank=True, null=True)

class Stream(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stream_id = models.CharField(max_length=64)
    streamer = models.ForeignKey(Streamer, on_delete=models.CASCADE, related_name='streams')
    game_id = models.CharField(max_length=64)
    game_name = models.CharField(max_length=64)
    type = models.CharField(max_length=32)
    title = models.CharField(max_length=255)
    viewer_count = models.IntegerField()
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    language = models.CharField(max_length=16)
    thumbnail_url = models.CharField(max_length=255)
    tag_ids = models.CharField(max_length=255, null=True, blank=True)
    is_mature = models.BooleanField()

    class Meta:
        ordering = ['-started_at']
