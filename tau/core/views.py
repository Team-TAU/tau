import os
import requests

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth import login
from django.conf import settings

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets

from constance import config

from tau.users.models import User
from .forms import ChannelNameForm, FirstRunForm

def home_view(request):
    user_count = User.objects.all().count()
    if user_count == 0:
        return HttpResponseRedirect('/first-run/')
    elif not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    elif config.CHANNEL == '':
        return HttpResponseRedirect('/set-channel/')
    elif config.SCOPE_UPDATED_NEEDED:
        return HttpResponseRedirect('/refresh-token-scope/')
    else:
        template = loader.get_template('home.html')
        return HttpResponse(template.render({}, request))

def first_run_view(request):
    user_count = User.objects.all().count()
    if user_count > 0:                      # If users already exist, it is not first run
        return HttpResponseRedirect('/')    # reject creating a new super-user
    if request.method == 'POST':
        form = FirstRunForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            user.is_superuser=True
            user.is_staff=True
            user.save()
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            template = loader.get_template('registration/first-run.html')
            return HttpResponse(template.render({}, request))
    else:
        template = loader.get_template('registration/first-run.html')
        return HttpResponse(template.render({}, request))

@api_view()
def channel_point_rewards(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged into access this endpoint.'})
    client_id = os.environ.get('TWITCH_APP_ID', None)
    headers = {
        'Authorization': 'Bearer {}'.format(config.TWITCH_ACCESS_TOKEN),
        'Client-Id': client_id
    }
    url = f'https://api.twitch.tv/helix/' \
          f'channel_points/custom_rewards?broadcaster_id={config.CHANNEL_ID}'

    rewards_r = requests.get(
        url,
        headers=headers
    )
    rewards_data = rewards_r.json()
    return JsonResponse(rewards_data)

@api_view()
def get_twitch_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged into access this endpoint.'})
    login_search=request.GET['login']
    client_id = os.environ.get('TWITCH_APP_ID', None)
    headers = {
        'Authorization': 'Bearer {}'.format(config.TWITCH_ACCESS_TOKEN),
        'Client-Id': client_id
    }
    url = f'https://api.twitch.tv/helix/' \
          f'users?login={login_search}'
    user_r = requests.get(
        url,
        headers=headers
    )
    user_data = user_r.json()
    return JsonResponse(user_data)

def get_streams(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged into access this endpoint.'})
    client_id = os.environ.get('TWITCH_APP_ID', None)
    headers = {
        'Authorization': 'Bearer {}'.format(config.TWITCH_ACCESS_TOKEN),
        'Client-Id': client_id
    }
    user_login = request.GET['user_login']
    url = f'https://api.twitch.tv/helix/' \
          f'streams?user_login={user_login}'
    data = requests.get(
        url,
        headers=headers
    )
    stream_data = data.json()
    return JsonResponse(stream_data)

def get_channel_name_view(request):
    if request.method == 'POST':
        port = os.environ.get('PORT', 8000)
        form = ChannelNameForm(request.POST)
        if form.is_valid():
            # Process the data
            config.CHANNEL = form.cleaned_data['channel_name']
            scope=' '.join(settings.TOKEN_SCOPES)
            client_id = os.environ.get('TWITCH_APP_ID', None)
            url = f'https://id.twitch.tv/oauth2/authorize?' \
                  f'client_id={client_id}&' \
                  f'redirect_uri={settings.BASE_URL}/twitch-callback/&' \
                  f'response_type=code&' \
                  f'scope={scope}'
            return HttpResponseRedirect(url)
        else:
            # Show some error page
            pass
    else:
        template = loader.get_template('registration/twitch-channel-setup.html')
        return HttpResponse(template.render({}, request))

def refresh_token_scope(request):
    client_id = os.environ.get('TWITCH_APP_ID', None)
    scope=' '.join(settings.TOKEN_SCOPES)
    url = f'https://id.twitch.tv/oauth2/authorize?' \
        f'client_id={client_id}&' \
        f'redirect_uri={settings.BASE_URL}/twitch-callback/&' \
        f'response_type=code&' \
        f'scope={scope}'
    return HttpResponseRedirect(url)

@api_view()
def get_tau_token(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged into access this endpoint.'})
    else:
        token = Token.objects.get(user=request.user)
        return JsonResponse({'token': token.key})

def process_twitch_callback_view(request):
    port = os.environ.get('PORT', 8000)
    params = request.GET
    auth_code = params['code']
    client_id = os.environ.get('TWITCH_APP_ID', None)
    client_secret = os.environ.get('TWITCH_CLIENT_SECRET', None)
    auth_r = requests.post('https://id.twitch.tv/oauth2/token', data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': f'{settings.BASE_URL}/twitch-callback/'
    })
    response_data = auth_r.json()
    config.TWITCH_ACCESS_TOKEN = response_data['access_token']
    config.TWITCH_REFRESH_TOKEN = response_data['refresh_token']

    scope=' '.join(settings.TOKEN_SCOPES)
    app_auth_r = requests.post('https://id.twitch.tv/oauth2/token', data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': scope
    })
    app_auth_data = app_auth_r.json()
    config.TWITCH_APP_ACCESS_TOKEN = app_auth_data['access_token']
    config.SCOPE_UPDATED_NEEDED = False
    headers = {
        'Authorization': 'Bearer {}'.format(config.TWITCH_ACCESS_TOKEN),
        'Client-Id': client_id
    }
    user_r = requests.get('https://api.twitch.tv/helix/users', headers=headers)
    user_data = user_r.json()
    channel_id = user_data['data'][0]['id']
    config.CHANNEL_ID = channel_id
    return HttpResponseRedirect('/')

class HeartbeatViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def list(self, request, *args, **kwargs):
        response = {'message': 'pong'}
        return Response(response)
