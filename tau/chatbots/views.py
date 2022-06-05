import os
from uuid import uuid4
import requests
import datetime

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from constance import config

from .models import ChatBot, ChatBotChannel
from .serializers import ChatBotChannelSerializer, ChatBotSerializer

# Create your views here.
class ChatBotViewSet(viewsets.ModelViewSet):
    queryset = ChatBot.objects.all()
    serializer_class = ChatBotSerializer
    permission_classes = (IsAuthenticated, )

    @action(methods=['GET'], detail=False, url_path='twitch-auth-link')
    def twitch_auth_link(self, request):
        state = uuid4()
        config.TWITCH_AUTH_STATE = str(state)
        client_id = os.environ.get('TWITCH_APP_ID', None)
        scope = 'chat:read chat:edit channel:moderate'
        url = f'https://id.twitch.tv/oauth2/authorize?' \
            f'client_id={client_id}&' \
            f'redirect_uri={settings.BASE_URL}/api/v1/chat-bots/twitch-callback/&' \
            f'response_type=code&' \
            f'scope={scope}&' \
            f'state={state}&' \
            f'force_verify=true'
        return Response({
            'url': url
        })

    @action(methods=['GET'], detail=False, url_path='twitch-callback/', permission_classes=[AllowAny])
    def twitch_callback(self, request):
        port = os.environ.get('PORT', 8000)
        params = request.GET
        auth_code = params['code']
        state = params.get('state', None)
        print(f'state: {state}')
        print(f'stored: {config.TWITCH_AUTH_STATE}')
        if state != config.TWITCH_AUTH_STATE:
            return HttpResponseForbidden()
        client_id = os.environ.get('TWITCH_APP_ID', None)
        client_secret = os.environ.get('TWITCH_CLIENT_SECRET', None)
        auth_r = requests.post('https://id.twitch.tv/oauth2/token', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': f'{settings.BASE_URL}/api/v1/chat-bots/twitch-callback/'
        })
        response_data = auth_r.json()
        access_token = response_data['access_token']
        refresh_token = response_data['refresh_token']
        expiration = timezone.now() + datetime.timedelta(seconds=response_data['expires_in'])

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Client-Id': client_id
        }
        user_req = requests.get('https://api.twitch.tv/helix/users', headers=headers)
        # if(settings.DEBUG_TWITCH_CALLS):
        #     log_request(user_r)
        user_data = user_req.json()['data'][0]

        if user_data['id'] == config.CHANNEL_ID:
            # Handle the user accidentally overwote all of our TAU scopes.
            # Show error and have user re-auth.
            return HttpResponse("You attempted to create a bot that is your streamer account.  Please go back to your other browser window and try again, but this time log in as your bot account.")

        # TODO: if creating bot that already exists, figure out what to do
        #       with the existing token/refresh token.  For now, simply overwrite
        #       the old token.  I think this is the right thing to do.

        instance, created = ChatBot.objects.update_or_create(
            user_name=user_data['display_name'],
            user_id=user_data['id'],
            user_login=user_data['login'],
            access_token=access_token,
            refresh_token=refresh_token,
            token_expiration=expiration
        )

        return HttpResponse(f'The bot named {user_data["display_name"]} is now authorized.  You may close this window.')


class ChatBotChannelViewSet(viewsets.ModelViewSet):
    queryset = ChatBotChannel.objects.all()
    serializer_class = ChatBotChannelSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = None
