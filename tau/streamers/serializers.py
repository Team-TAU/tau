from rest_framework import serializers
from .models import Streamer

class StreamerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streamer
        fields = (
            'id',
            'twitch_username',
            'twitch_id',
            'streaming',
            'disabled',
            'created',
            'updated',
        )
        read_only_fields = ('id', 'twitch_id', 'created', 'updated',)
