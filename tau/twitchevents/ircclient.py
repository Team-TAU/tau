import pprint

import time
import datetime
import json

import requests

import websockets
import asyncio

from django.utils import timezone
from django.conf import settings

from constance import config
from channels.db import database_sync_to_async

from .models import TwitchEvent
from .serializers import TwitchEventSerializer

class IRCClient():
    url = 'wss://irc-ws.chat.twitch.tv'
    connection = None
    loop = None
    tasks = []

    def __init__(self, token):
        self.tau_token = token

    async def connect(self):
        delay = 1
        while True:
            self.connection = await websockets.client.connect(self.url)
            if self.connection.open:
                print('---- Connected to twitch irc ws server ----')
                await self.initial_connect()
                break
            else:
                print(f'---- Could not connect, waiting {delay}s to reconnect ----')
                await asyncio.sleep(delay)
                if delay < 120:
                    delay = max(delay*2, 120)

    def create_event_loop(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.connect())
        self.tasks = [
            asyncio.ensure_future(self.recieve()),
            asyncio.ensure_future(self.check_irc_settings())
        ]
        self.loop.run_until_complete(asyncio.wait(self.tasks))

    def clear_event_loop(self):
        for t in self.tasks:
            t.cancel()
            t = None
        self.tasks = []

    def run(self):
        self.token = config.TWITCH_ACCESS_TOKEN
        self.username = config.CHANNEL
        while True:
            if config.USE_IRC:
                try:
                    self.create_event_loop()
                except RuntimeError:
                    # RuntimeError can occur when we interrupt the event_loop, if the
                    # config.USE_IRC value is set to False by the user
                    pass
            else:
                self.clear_event_loop()
                while not config.USE_IRC:
                    time.sleep(5)

    async def initial_connect(self):
        caps = 'twitch.tv/tags twitch.tv/commands twitch.tv/membership'
        await self.connection.send(f'CAP REQ :{caps}')
        await self.connection.send(f'PASS oauth:{self.token}')
        await self.connection.send(f'NICK {self.username}')
        await self.connection.send(f'JOIN #{self.username.lower()}')

    async def recieve(self):
        # pp = pprint.PrettyPrinter(indent=2)
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

    async def check_irc_settings(self): 
        while True:
            await asyncio.sleep(5)
            use_irc = await database_sync_to_async(self.lookup_setting)('USE_IRC')
            if not use_irc and self.loop.is_running():
                await self.connection.close()
                print('---- Disconnected from twitch irc ws server ----')
                self.loop.stop()

    def lookup_setting(self, setting):
        return getattr(config, setting)

    def handle_channel_points(self, data):
        start_time = timezone.now() - datetime.timedelta(seconds=2)

        time.sleep(1)
        redemption = TwitchEvent.objects.filter(
            event_type='point-redemption',
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



