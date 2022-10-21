from rest_framework import serializers
from .models import TwitchEvent

class TwitchEventSerializer(serializers.ModelSerializer):
    origin = serializers.SerializerMethodField()

    def get_origin(self, obj):
        return 'twitch'

    class Meta:
        model = TwitchEvent
        fields = (
            'id',
            'event_id',
            'event_type',
            'event_source',
            'event_data',
            'created',
            'origin',
        )
        read_only_fields = ('id', 'created', )
