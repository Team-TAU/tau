import asyncio
import datetime
import time
import json

from django.conf import settings
from django.utils import timezone

import requests
import websockets

from channels.db import database_sync_to_async

from tau.core.utils import lookup_setting, parse_message
from tau.twitchevents.models import TwitchEvent
from tau.twitchevents.serializers import TwitchEventSerializer

class WorkerIrc:
    irc_url = 'wss://irc-ws.chat.twitch.tv'
    connected = False
    streamer = False
    connection = None
    token_refreshed = False
    tau_token = None
    bot = None
    username = ''
    channels = []
    irc_delay = 2.5
    subscribers = 0

    def __init__(self, tau_token, streamer=None, bot=None):
        self.tau_token = tau_token
        self.streamer = streamer
        if self.streamer is None:
            self.bot = bot
            self.username = bot.user_name
            self.user_login = bot.user_login
            self.channels = [channel.channel for channel in bot.channels.all()]
        else:
            self.streamer = True
            self.username = streamer
            self.user_login = streamer.lower()
            self.channels = [f'#{self.username.lower()}']

    def get_channels(self):
        if self.streamer is None:
            return [channel.channel for channel in self.bot.channels.all()]
        else:
            return [f'#{self.username.lower()}']

    def subscribe(self):
        self.subscribers += 1

    async def unsubscribe(self):
        self.subscribers -= 1
        if self.subscribers == 0:
            await self.disconnect()
            print(f'     [Disconnected from IRC for {self.bot.user_name}]')
            self.connected = False

    async def should_connect(self):
        use_irc = await database_sync_to_async(lookup_setting)('USE_IRC')
        return (self.streamer and use_irc) or (not self.streamer and self.subscribers > 0)

    async def manage_irc_loop(self):
        while True:
            should_connect = await self.should_connect()
            if should_connect and not self.connected:
                await self.connect_irc()
            await asyncio.sleep(self.irc_delay)

    async def connect_irc(self):
        await self.connect()
        await self.receive()

    def set_token_refreshed(self):
        self.token_refreshed = True

    async def disconnect(self):
        await self.connection.close()

    async def connect(self):
        delay = 1
        while True:
            while self.streamer and not self.token_refreshed:
                await asyncio.sleep(0.5)
            self.connection = await websockets.client.connect(self.irc_url)
            if self.connection.open:
                print(f'     [Opening IRC Connection for {self.username}]')
                await self.initial_connect()
                print(f'     [Connected to IRC for {self.username}]')
                self.connected = True
                break
            else:
                print(f'---- Could not connect, waiting {delay}s to reconnect ----')
                await asyncio.sleep(delay)
                if delay < 120:
                    delay = max(delay*2, 120)

    async def send(self, channel, message):
        await self.connection.send(f'PRIVMSG #{channel} :{message}')

    async def receive(self):
        while True:
            try:
                message = await self.connection.recv()
                data = parse_message(message)
                # pp.pprint(data)
                if self.streamer and 'custom-reward-id' in data['tags']:
                    await database_sync_to_async(self.handle_channel_points)(data)
                elif data['command'] == "PRIVMSG":
                    payload = {
                        "irc_username": self.user_login,
                        "data": data
                    }
                    headers = {
                        'Authorization': f'Token {self.tau_token}',
                        'Content-type': 'application/json'
                    }
                    requests.post(
                        f'{settings.LOCAL_URL}/api/v1/irc',
                        json=payload,
                        headers=headers
                    )
                elif data['prefix'] is None and data['command'] == 'PING':
                    await self.connection.send('PONG')

            except websockets.exceptions.ConnectionClosed:
                should_connect = await self.should_connect()
                if should_connect:
                    print('Websocket to twitch irc unexpectedly closed... reconnecting')
                    await self.connect()
                else:
                    break

    async def keep_alive(self):
        payload = {
            "irc_username": self.user_login,
            "data": {'command': 'keep_alive'}
        }
        headers = {
            'Authorization': f'Token {self.tau_token}',
            'Content-type': 'application/json'
        }
        requests.post(
            f'{settings.LOCAL_URL}/api/v1/irc',
            json=payload,
            headers=headers
        )

    async def initial_connect(self):
        if self.streamer:
            token = await database_sync_to_async(lookup_setting)('TWITCH_ACCESS_TOKEN')
        else:
            if self.bot.is_token_expired():
                await database_sync_to_async(self.bot.renew_token)()
            token = self.bot.access_token

        caps = 'twitch.tv/tags twitch.tv/commands twitch.tv/membership'
        await self.connection.send(f'CAP REQ :{caps}')
        await self.connection.send(f'PASS oauth:{token}')
        await self.connection.send(f'NICK {self.user_login}')
        for channel in self.channels:
            await self.join_channel(channel)

    async def add_channel(self, channel):
        self.channels.append(channel)
        if self.connected:
            await self.join_channel(channel)

    async def remove_channel(self, channel):
        if self.connected:
            await self.part_channel(channel)
        self.channels.remove(channel)

    async def part_channel(self, channel):
        # await self.connection.send(f'PRIVMSG {channel} :Goodbye!  I am leaving.')
        await self.connection.send(f'PART {channel}')

    async def join_channel(self, channel):
        await self.connection.send(f'JOIN {channel}')
        # await self.connection.send(f'PRIVMSG {channel} :Hello Chat!  I am alive!')

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
