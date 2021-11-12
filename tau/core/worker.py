from os import truncate
import time
import datetime
import json

import requests

from pyngrok import ngrok

import websockets
import asyncio

from django.utils import timezone
from django.conf import settings

from constance import config
from channels.db import database_sync_to_async
from tau.streamers.utils import update_all_streamers

from tau.twitchevents.models import TwitchEvent
from tau.twitchevents.serializers import TwitchEventSerializer

from .utils import (
    setup_ngrok,
    init_webhooks,
    refresh_access_token,
    teardown_all_acct_webhooks,
    teardown_webhooks,
    get_active_event_sub_ids,
    get_active_streamer_sub_ids
)

class Worker():
    irc_url = 'wss://irc-ws.chat.twitch.tv'
    connection = None
    loop = None
    tasks = []
    irc_connected = False
    wh_delay = 15
    irc_delay = 2
    active_event_sub_ids = []
    active_streamer_sub_ids = []
    ngrok_tunnel = None
    token_refreshed = False

    def __init__(self, token):
        self.tau_token = token

    def setup_webhooks(self):
        twitch_access_token = config.TWITCH_APP_ACCESS_TOKEN
        if twitch_access_token != '':
            print(f'---- Establishing IRC and Webhook Connections ----')
            refresh_access_token()  # refresh the access token
            self.token_refreshed = True
            print('     [Access tokens refreshed]')
            if not config.RESET_ALL_WEBHOOKS:
                
                teardown_webhooks(self.tau_token)
                print('     [Old WebHooks torn down]')
            else:
                print('     [Tearing down all webhooks]')
                teardown_webhooks(self.tau_token)
                teardown_all_acct_webhooks()
                config.RESET_ALL_WEBHOOKS = False
            self.active_event_sub_ids, self.active_streamer_sub_ids = init_webhooks(self.public_url, self.tau_token)
            print('     [New WebHooks Initialized]')
            update_all_streamers()
            print('     [All streamer statuses updated]\n')
        else:
            print(
                'You have not yet set up a username, or authorized TAU to connect '
                'to your twitch account.  Webhooks will be set up after you do so.'
            )

    async def connect(self):
        delay = 1
        while True:
            if self.token_refreshed:
                self.connection = await websockets.client.connect(self.irc_url)
                if self.connection.open:
                    print('     [Opening IRC Connection]')
                    await self.initial_connect()
                    print('     [Connected to IRC]')
                    self.irc_connected = True
                    break
                else:
                    print(f'---- Could not connect, waiting {delay}s to reconnect ----')
                    await asyncio.sleep(delay)
                    if delay < 120:
                        delay = max(delay*2, 120)
            else:
                await asyncio.sleep(delay)

    def create_event_loop(self):
        self.loop = asyncio.get_event_loop()
        self.tasks = [
            asyncio.ensure_future(self.manage_webhooks()),
            asyncio.ensure_future(self.manage_irc_loop()),
            asyncio.ensure_future(self.check_irc_settings()),
        ]
        self.loop.run_until_complete(asyncio.wait(self.tasks))

    async def manage_irc_loop(self):
        while True:
            use_irc = await database_sync_to_async(self.lookup_setting)('USE_IRC')
            if use_irc and not self.irc_connected:
                await self.connect_irc()

            await asyncio.sleep(self.irc_delay)

    async def connect_irc(self):
        await self.connect()
        await self.recieve()

    def disconnect_irc(self):
        pass

    async def manage_webhooks(self):
        refresh_webhooks = True
        while True:
            refreshed_ngrok = False
            if settings.USE_NGROK and self.ngrok_tunnel is None:
                self.public_url, self.ngrok_tunnel = await database_sync_to_async(setup_ngrok)()
                refreshed_ngrok = True
            elif settings.USE_NGROK:
                # Check to see if tunnel is still alive
                r = requests.get(f'{self.public_url}/api/v1/heartbeat')
                if r.status_code != 200:
                    try:
                        ngrok.disconnect(self.ngrok_tunnel.public_url)
                    except:
                        pass

                    self.public_url, self.ngrok_tunnel = await database_sync_to_async(setup_ngrok)()
                    refreshed_ngrok = True
            else:
                self.public_url = settings.BASE_URL
                await database_sync_to_async(self.set_setting)('PUBLIC_URL', settings.BASE_URL)
            # check for difference in required webhooks:
            new_event_sub_ids = await database_sync_to_async(get_active_event_sub_ids)()
            scopes_refreshed = await database_sync_to_async(self.lookup_setting)('SCOPES_REFRESHED')
            if set(self.active_event_sub_ids) != set(new_event_sub_ids) and scopes_refreshed:
                refresh_webhooks = True
                await database_sync_to_async(self.set_setting)('SCOPES_REFRESHED', False)

            if refresh_webhooks or refreshed_ngrok:
                await database_sync_to_async(self.setup_webhooks)()
                refresh_webhooks = False
            
            force_refresh_webhooks = await database_sync_to_async(self.lookup_setting)('FORCE_WEBHOOK_REFRESH')

            if force_refresh_webhooks:
                await database_sync_to_async(self.setup_webhooks)()
                await database_sync_to_async(self.set_setting)('FORCE_WEBHOOK_REFRESH', False)

            await asyncio.sleep(self.wh_delay)

    def run(self):
        self.token = config.TWITCH_ACCESS_TOKEN
        self.username = config.CHANNEL
        self.create_event_loop()

    async def initial_connect(self):
        token = await database_sync_to_async(self.lookup_setting)('TWITCH_ACCESS_TOKEN')
        caps = 'twitch.tv/tags twitch.tv/commands twitch.tv/membership'
        await self.connection.send(f'CAP REQ :{caps}')
        await self.connection.send(f'PASS oauth:{token}')
        await self.connection.send(f'NICK {self.username}')
        await self.connection.send(f'JOIN #{self.username.lower()}')

    async def recieve(self):
        while True:
            try:
                message = await self.connection.recv()
                data = self.parse_message(message)
                # pp.pprint(data)
                if 'custom-reward-id' in data['tags']:
                    await database_sync_to_async(self.handle_channel_points)(data)
                elif data['prefix'] is None and data['command'] == 'PING':
                    await self.connection.send('PONG')
                
            except websockets.exceptions.ConnectionClosed:
                use_irc = await database_sync_to_async(self.lookup_setting)('USE_IRC')
                if use_irc:
                    print('Websocket to twitch irc unexpectedly closed... reconnecting')
                    await self.connect()
                else:
                    break

    async def check_irc_settings(self): 
        while True:
            await asyncio.sleep(self.irc_delay)
            use_irc = await database_sync_to_async(self.lookup_setting)('USE_IRC')
            if not use_irc and self.irc_connected:
                await self.connection.close()
                self.irc_connected = False
                print('---- Disconnected from twitch irc ws server ----')

    def lookup_setting(self, setting):
        return getattr(config, setting)

    def set_setting(self, setting, value):
        setattr(config, setting, value)

    def handle_channel_points(self, data):
        start_time = timezone.now() - datetime.timedelta(seconds=2)

        time.sleep(1)
        redemption = TwitchEvent.objects.filter(
            event_type='channel-channel_points_custom_reward_redemption-add',
            created__gte=start_time,
            event_data__user_login=data['tags']['display-name'].lower()
        )
        if redemption.exists():
            redemption = redemption.first()
            redemption.event_data['user_input_emotes'] = data['tags']['emotes']
            serializer = TwitchEventSerializer(redemption, many=False)
            headers = {
                'Authorization': f'Token {self.tau_token}',
                'Content-type': 'application/json'
            }
            requests.put(
                f'{settings.LOCAL_URL}/api/v1/twitch-events/{redemption.id}',
                data=json.dumps(serializer.data),
                headers=headers
            )

        return

    def parse_message(self, data):
        message = {
            'raw': data,
            'tags': {},
            'prefix': None,
            'command': None,
            'params': [],
            'message-text': None
        }

        position = 0
        nextspace = 0

        if data[0] == '@':
            nextspace = data.find(' ')
            if(nextspace == -1):
                return None

            rawTags = data[1:nextspace].split(';')
            for tag in rawTags:
                pair = tag.split('=')
                if len(pair) == 1:
                    value = True
                else:
                    value = pair[1]
                message['tags'][pair[0]] = value
            position = nextspace + 1

            while data[position] == ' ':
                position += 1
            
        if data[position] == ':':
            nextspace = data.find(' ', position)

            if nextspace == -1:
                return None
            
            message['prefix'] = data[position:nextspace]

            position = nextspace + 1

            while data[position] == ' ':
                position += 1

        nextspace = data.find(' ', position)

        if nextspace == -1:
            if len(data) > position:
                message['command'] = data[position:]
            else:
                message['command'] = None
            return message
        
        message['command'] = data[position:nextspace]

        while data[position] == ' ':
            position+=1
        
        while position < len(data):
            nextspace = data.find(' ', position)
            if data[position] == ':':
                message['params'].append(data[position:])
                break

            if nextspace != -1:
                message['params'].append(data[position:nextspace])
                position = nextspace + 1

                while data[position] == ' ':
                    position += 1
                
                continue
        
            if nextspace == -1:
                message['params'].append(data[position:])
                break
        
        if message['command'] == 'PRIVMSG':
            message['message-text'] = message['params'][2][1:].replace("\n", "").replace("\r", "")

        if 'emotes' in message['tags']:
            emotes = message['tags']['emotes']
            emote_list = []
            if emotes != '':
                for emote_txt in emotes.split('/'):
                    emote_data=emote_txt.split(':')
                    emote_list.append({
                        'id': emote_data[0],
                        'positions': [
                            [int(val) for val in position.split('-')]
                            for position in emote_data[1].split(',')
                        ]
                    })
            message['tags']['emotes'] = emote_list

        return message
