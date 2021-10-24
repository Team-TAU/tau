import os
import requests
import datetime

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.template import loader
from django.contrib.auth import login
from django.conf import settings
from django.http import Http404
from django.utils import timezone
import rest_framework

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import viewsets

from constance import config
import constance.settings

from tau.twitch.models import TwitchAPIScope, TwitchEventSubSubscription
from tau.users.models import User
from .forms import ChannelNameForm, FirstRunForm
from  .utils import log_request, check_access_token_expired, refresh_access_token
from tau.twitch.models import TwitchHelixEndpoint

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def helix_view(request, helix_path=None):
    if check_access_token_expired():
        refresh_access_token()
    try:
        endpoint_instance = TwitchHelixEndpoint.objects.get(
            endpoint=helix_path,
            method=request.method
        )
        if endpoint_instance.token_type == 'OA':
            token = config.TWITCH_ACCESS_TOKEN
        else:
            token = config.TWITCH_APP_ACCESS_TOKEN
    except TwitchHelixEndpoint.DoesNotExist:
        token = config.TWITCH_ACCESS_TOKEN
    body = request.data
    client_id = os.environ.get('TWITCH_APP_ID', None)
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Client-Id': client_id
    }
    
    url = f'https://api.twitch.tv/helix/' \
          f'{helix_path}'
    uri = request.build_absolute_uri()
    url_params = ''
    if uri.count('?') > 0:
        url_params = uri.split('?', 1)[1]
    if url_params != '':
        url += f'?{url_params}'
    
    if request.method == 'GET':
        data = requests.get(
            url,
            headers=headers
        )
    elif request.method == 'POST':
        data = requests.post(
            url,
            data=body,
            headers=headers
        )
    elif request.method == 'PUT':
        data = requests.put(
            url,
            data=body,
            headers=headers
        )
        print(data)
    elif request.method == 'PATCH':
        data = requests.patch(
            url,
            data=body,
            headers=headers
        )
    elif request.method == 'DELETE':
        data = requests.delete(
            url,
            headers=headers
        )
    try:
        if(settings.DEBUG_TWITCH_CALLS):
            log_request(data)
        stream_data = data.json()
    except ValueError:
        stream_data = None

    return Response(stream_data, status=data.status_code)

def home_view(request):
    user_count = User.objects.all().exclude(username='worker_process').count()
    if user_count == 0:
        return HttpResponseRedirect('/first-run/')
    # elif not request.user.is_authenticated:
    #     return HttpResponseRedirect('/accounts/login/')
    elif config.CHANNEL == '':
        return HttpResponseRedirect('/set-channel/')
    elif config.SCOPE_UPDATED_NEEDED:
        return HttpResponseRedirect('/refresh-token-scope/')
    else:
        # # template = loader.get_template('home.html')
        # template = loader.get_template('dashboard/index.html')
        # return HttpResponse(template.render({'config': config}, request))
        return HttpResponseRedirect('/dashboard')

def first_run_view(request):
    user_count = User.objects.all().exclude(username='worker_process').count()
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
                  f'scope={scope}&' \
                  f'force_verify=true'
            return HttpResponseRedirect(url)
        else:
            # Show some error page
            pass
    else:
        template = loader.get_template('registration/twitch-channel-setup.html')
        return HttpResponse(template.render({}, request))

def refresh_token_scope(request):
    client_id = os.environ.get('TWITCH_APP_ID', None)

    helix_scopes = list(
        TwitchAPIScope.objects.filter(
            required=True
        ).values_list('scope', flat=True)
    )
    eventsub_scopes = list(
        TwitchEventSubSubscription.objects.filter(
            active=True
        ).values_list('scope_required', flat=True)
    )
    scopes = list(set(settings.TOKEN_SCOPES + eventsub_scopes + helix_scopes))
    scopes = list(filter(lambda x: (x is not None), scopes))
    scope=' '.join(scopes)

    url = f'https://id.twitch.tv/oauth2/authorize?' \
        f'client_id={client_id}&' \
        f'redirect_uri={settings.BASE_URL}/twitch-callback/&' \
        f'response_type=code&' \
        f'scope={scope}&' \
        f'force_verify=true'
    return HttpResponseRedirect(url)

@api_view()
def get_tau_token(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged into access this endpoint.'})
    else:
        token = Token.objects.get(user=request.user)
        return JsonResponse({'token': token.key})

@api_view(['POST'])
def refresh_tau_token(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged into access this endpoint.'})
    else:
        token = Token.objects.get(user=request.user)
        token.delete()
        token = Token.objects.create(user=request.user)

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
    if(settings.DEBUG_TWITCH_CALLS):
        log_request(auth_r)
    config.TWITCH_ACCESS_TOKEN = response_data['access_token']
    config.TWITCH_REFRESH_TOKEN = response_data['refresh_token']
    expiration = timezone.now() + datetime.timedelta(seconds=response_data['expires_in'])
    config.TWITCH_ACCESS_TOKEN_EXPIRATION = expiration
    scope=' '.join(settings.TOKEN_SCOPES)
    app_auth_r = requests.post('https://id.twitch.tv/oauth2/token', data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': scope
    })
    if(settings.DEBUG_TWITCH_CALLS):
        log_request(app_auth_r)
    app_auth_data = app_auth_r.json()
    config.TWITCH_APP_ACCESS_TOKEN = app_auth_data['access_token']
    config.SCOPE_UPDATED_NEEDED = False
    config.SCOPES_REFRESHED = True
    headers = {
        'Authorization': 'Bearer {}'.format(config.TWITCH_ACCESS_TOKEN),
        'Client-Id': client_id
    }
    user_r = requests.get('https://api.twitch.tv/helix/users', headers=headers)
    if(settings.DEBUG_TWITCH_CALLS):
        log_request(user_r)
    user_data = user_r.json()
    channel_id = user_data['data'][0]['id']
    config.CHANNEL_ID = channel_id
    return HttpResponseRedirect('/')


class HeartbeatViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def list(self, request, *args, **kwargs):
        response = {'message': 'pong'}
        return Response(response)


class TAUSettingsViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )

    valid_keys = ['USE_IRC']

    def list(self, request, *args, **kwargs):
        response = {key.lower(): getattr(config, key) for key in self.valid_keys}
        return Response(response)

    def retrieve(self, request, pk=None):
        if pk.upper() in self.valid_keys:
            return Response({pk: getattr(config, pk.upper())})
        else:
            raise Http404

    def update(self, request, pk=None):
        if pk.upper() in self.valid_keys:
            data = request.data
            setattr(config, pk.upper(), data['value'])
            return Response({pk: data['value']})
        else:
            raise Http404


class ServiceStatusViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )

    def update(self, request, pk=None):
        if pk.startswith('STATUS_') and hasattr(config, pk):
            data = request.data
            new_status = data['status']
            setattr(config, pk, new_status)
            return Response({
                pk: new_status
            })
        elif pk == 'SET_ALL':
            status_keys = filter(
                lambda x: x.startswith('STATUS_'),
                constance.settings.CONFIG.keys()
            )
            data = request.data
            new_status = data['status']
            for key in status_keys:
                setattr(config, key, new_status)
            return Response({
                'reset': 'complete'
            })
        else:
            raise Http404("Config does not exist")
