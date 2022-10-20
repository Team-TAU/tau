import os

import requests

from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    JsonResponse,
    Http404
)
from django.template import loader
from django.contrib.auth import login
from django.conf import settings

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import viewsets, status
from rest_framework.decorators import action

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from constance import config
import constance.settings

from tau.twitch.models import TwitchAPIScope, TwitchEventSubSubscription
from tau.users.models import User
from tau.twitch.models import TwitchHelixEndpoint

from .forms import ChannelNameForm, FirstRunForm
from .utils import (
    cleanup_remote_webhooks,
    cleanup_webhooks,
    handle_tau_bot_token,
    handle_tau_streamer_token,
    log_request,
    check_access_token_expired,
    refresh_access_token,
    teardown_all_acct_webhooks,
)

@api_view(['POST'])
def irc_message_view(request):
    payload = request.data
    bot_user_login = payload.get("irc_username", "")

    # bot = ChatBot.objects.get(user_login=bot_user_login)
    channel_layer = get_channel_layer()
    print(request.data)
    if request.data['data'].get('command', None) == 'keep_alive':
        print("Sending keepalive!")
        async_to_sync(channel_layer.group_send)(
            f'chat_bot__{bot_user_login}',
            {
                'type': 'chatbot.keepalive',
                'data': None
            }
        )
    else:
        async_to_sync(channel_layer.group_send)(
            f'chat_bot__{bot_user_login}',
            {
                'type': 'chatbot.event',
                'data': request.data
            }
        )
    return Response({}, status=status.HTTP_201_CREATED)

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
    client_id = settings.TWITCH_CLIENT_ID
    headers = {
        'Authorization': f'Bearer {token}',
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
            json=body,
            headers=headers
        )
    elif request.method == 'PUT':
        data = requests.put(
            url,
            json=body,
            headers=headers
        )
    elif request.method == 'PATCH':
        data = requests.patch(
            url,
            json=body,
            headers=headers
        )
    elif request.method == 'DELETE':
        data = requests.delete(
            url,
            headers=headers
        )
    try:
        if settings.DEBUG_TWITCH_CALLS:
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
            user.is_superuser = True
            user.is_staff = True
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
        form = ChannelNameForm(request.POST)
        if form.is_valid():
            # Process the data
            config.CHANNEL = form.cleaned_data['channel_name']
            scope = ' '.join(settings.TOKEN_SCOPES)
            client_id = settings.TWITCH_CLIENT_ID
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
    client_id = settings.TWITCH_CLIENT_ID

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
    scope = ' '.join(scopes)

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

@api_view(['GET'])
def get_public_url(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged into access this endpoint.'})
    else:
        public_url = config.PUBLIC_URL
        return JsonResponse({'public_url': public_url})

@api_view(['POST'])
def refresh_tau_token(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged into access this endpoint.'})
    else:
        token = Token.objects.get(user=request.user)
        token.delete()
        token = Token.objects.create(user=request.user)

        return JsonResponse({'token': token.key})

@api_view(['POST'])
def reset_webhooks(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged into access this endpoint.'})
    data = request.data
    if data['type'] == 'all':
        teardown_all_acct_webhooks()
    elif data['type'] == 'remote':
        cleanup_remote_webhooks()
    elif data['type'] == 'broken':
        cleanup_webhooks()
    else:
        return JsonResponse({'webhooks_reset': False, 'error': 'Proper type not found.'})
    config.FORCE_WEBHOOK_REFRESH = True
    return JsonResponse({'webhooks_reset': True})

def authenticate_bot(request):
    params = request.GET
    bot_id = params['bot']
    client_id = settings.TWITCH_CLIENT_ID
    scope = 'chat:read chat:edit'

    url = f'https://id.twitch.tv/oauth2/authorize?' \
        f'client_id={client_id}&' \
        f'redirect_uri={settings.BASE_URL}/twitch-callback/&' \
        f'response_type=code&' \
        f'scope={scope}&' \
        f'state={bot_id}&' \
        f'force_verify=true'

    return HttpResponseRedirect(url)

def process_twitch_callback_view(request):
    params = request.GET
    auth_code = params['code']
    bot_id = params.get('state', None)
    client_id = settings.TWITCH_CLIENT_ID
    client_secret = os.environ.get('TWITCH_CLIENT_SECRET', None)
    auth_r = requests.post('https://id.twitch.tv/oauth2/token', data={
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': f'{settings.BASE_URL}/twitch-callback/'
    })
    response_data = auth_r.json()
    if settings.DEBUG_TWITCH_CALLS:
        log_request(auth_r)

    if bot_id is None:
        # We are setting up/refreshing the initial streamer and app
        # tokens
        handle_tau_streamer_token(response_data, client_id, client_secret)
        return HttpResponseRedirect('/')

    # We are setting up a bot token.
    handle_tau_bot_token(bot_id, response_data)
    return HttpResponseRedirect('/dashboard/chat-bots')

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

    @action(methods=['post'], detail=False, url_path='keep-alive')
    def keep_alive(self, request):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'taustatus',
            {
                'type': 'taustatus.keepalive',
                'data': None
            }
        )
        return Response({"sent": True})

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
