from rest_framework import serializers
from .models import (
    TwitchAPIScope,
    TwitchHelixEndpoint,
    TwitchEventSubSubscription
)

class TwitchEventSubSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitchEventSubSubscription
        fields = (
            'id',
            'name',
            'lookup_name',
            'subscription_type',
            'description',
            'active',
            'version',
            'scope_required',
            'status',
            'base_url',
            'subscription',
            'event_schema',
            'condition_schema',
        )
        read_only_fields = ('id',)


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
