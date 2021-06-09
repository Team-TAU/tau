from rest_framework import serializers
from .models import TwitchAPIScope, TwitchHelixEndpoint

class TwitchEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitchHelixEndpoint
        fields = (
            'id',
            'description',
            'endpoint',
            'method',
            'reference_url',
            'token_type',
            'scope'
        )
        read_only_fields = ('id',)


class TwitchAPIScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitchAPIScope
        fields = (
            'id',
            'scope',
            'required'
        )
        read_only_fields = ('id',)
