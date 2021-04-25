from rest_framework import serializers
from .models import Streamer, Stream

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

class StreamSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    user_login = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    def get_user_id(self, obj):
        return obj.streamer.twitch_id

    def get_user_login(self, obj):
        return obj.streamer.twitch_username.lower()

    def get_user_name(self, obj):
        return obj.streamer.twitch_username

    class Meta:
        model = Stream
        fields = (
            'id',
            'stream_id',
            'user_id',
            'user_login',
            'user_name',
            'game_id',
            'game_name',
            'type',
            'title',
            'viewer_count',
            'started_at',
            'ended_at',
            'language',
            'thumbnail_url',
            'tag_ids',
            'is_mature',
        )
