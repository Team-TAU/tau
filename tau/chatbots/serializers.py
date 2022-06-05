from rest_framework import serializers
from .models import ChatBot, ChatBotChannel


class ChatBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatBot
        fields = (
            'id',
            'user_name',
            'user_id',
            'user_login',
            'access_token',
            'refresh_token',
            'token_expiration',
            'connected',
            'created',
            'updated',
        )
        read_only_fields = ('id', 'created', 'updated', )


class ChatBotChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatBotChannel
        fields = ('id', 'channel', 'chat_bot',)
        read_only_fields = ('id',)
