import os
import datetime

import uuid
import requests

from django.db import models
from django.utils import timezone
from django.conf import settings


# Create your models here.
class ChatBot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255, unique=True)
    user_login = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    refresh_token = models.CharField(max_length=255, null=True, blank=True)
    token_expiration = models.DateTimeField(null=True, blank=True)
    connected = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Chat Bot({self.id}): {self.user_name}'

    def is_token_expired(self):
        return timezone.now() > self.token_expiration

    def renew_token(self):
        refresh_token = self.refresh_token
        client_id = settings.TWITCH_CLIENT_ID
        client_secret = os.environ.get('TWITCH_CLIENT_SECRET', None)
        req = requests.post('https://id.twitch.tv/oauth2/token', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        })
        # if(settings.DEBUG_TWITCH_CALLS):
        #     log_request(req)
        data = req.json()
        if 'access_token' in data:
            self.refresh_token = data['refresh_token']
            self.access_token = data['access_token']
            self.token_expiration = timezone.now() + datetime.timedelta(
                seconds=(data['expires_in']-60)
            )
            self.save()
        else:
            print('[ERROR] Could not refresh access token.')


class ChatBotChannel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.CharField(max_length=255)
    chat_bot = models.ForeignKey(ChatBot, on_delete=models.CASCADE, related_name='channels')
