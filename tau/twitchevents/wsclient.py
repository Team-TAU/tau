import asyncio
import json
from random import randrange
import requests
import websockets
from pyngrok import ngrok

from django.conf import settings

from channels.db import database_sync_to_async
from constance import config

from tau.core.apps import CoreConfig
from tau.core.utils import check_access_token, refresh_access_token
from .models import TwitchEvent


class WebSocketClient():
    url = 'wss://pubsub-edge.twitch.tv'
    connection = None

    def __init__(self):
        config.STATUS_WEBSOCKET = 'DISCONNECTED'
        channel_id = config.CHANNEL_ID
        auth_token = config.TWITCH_ACCESS_TOKEN
        self.points_topic = f"channel-points-channel-v1.{channel_id}"
        self.subscribe_topic = f"channel-subscribe-events-v1.{channel_id}"
        self.listen_message = {
            "type": "LISTEN",
            "nonce": "abcdTSFr32sfD",
            "data": {
                "topics": [
                    self.subscribe_topic,
                ],
                "auth_token": auth_token,
            }
        }
        self.ping_message = {
            "type": "PING"
        }

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.connect())
        tasks = [
            asyncio.ensure_future(self.twitch_heartbeat()),
            asyncio.ensure_future(self.recieve()),
            asyncio.ensure_future(self.token_check()),
        ]
        if settings.USE_NGROK:
            tasks.append(asyncio.ensure_future(self.ngrok_heartbeat()))
        loop.run_until_complete(asyncio.wait(tasks))

    async def connect(self):
        delay = 1
        await self.set_config('STATUS_WEBSOCKET', 'CONNECTING')
        while True:
            self.connection = await websockets.client.connect(self.url)
            if self.connection.open:
                print('---- Connected to twitch ws server ----')
                await self.connection.send(json.dumps(self.listen_message))
                await self.set_config('STATUS_WEBSOCKET', 'CONNECTED')
                break
            else:
                print(f'---- Could not connect, waiting {delay}s to reconnect ----')
                await self.set_config('STATUS_WEBSOCKET', 'RECONNECTING')
                await asyncio.sleep(delay)
                if delay < 120:
                    delay = max(delay*2, 120)

    async def twitch_heartbeat(self):
        while True:
            try:
                await self.connection.send(json.dumps(self.ping_message))
                delay = 60 + randrange(20)
                await asyncio.sleep(delay)
            except websockets.exceptions.ConnectionClosed:
                # Wait 10s to see if connection is re-established
                await asyncio.sleep(10)

    async def token_check(self):
        while True:
            token_valid = await database_sync_to_async(check_access_token)()
            if not token_valid:
                await database_sync_to_async(refresh_access_token)()
            delay = 60 + randrange(20)
            await asyncio.sleep(delay)

    async def ngrok_heartbeat(self):
        while True:
            try:
                r = requests.get(f'{settings.BASE_URL}/api/v1/heartbeat/')
                r.raise_for_status()
            except:  # pylint: disable=bare-except
                ngrok.kill() # need to kill ngrok process to start new one.
                print('---- WARNING ngrok tunnel down!  Re-establishing. ----')
                public_url = CoreConfig.setup_ngrok()
                await database_sync_to_async(CoreConfig.setup_webhooks)(public_url)

            delay = 5
            await asyncio.sleep(delay)

    async def recieve(self):
        while True:
            try:
                message = await self.connection.recv()
                message_dict = json.loads(message)
                if message_dict['type'] == 'MESSAGE':
                    await self.handle_data(message_dict['data'])
                elif message_dict['type'] == 'RECONNECT':
                    await self.handle_reconnect()
            except websockets.exceptions.ConnectionClosed:
                print('Websocket to twitch closed... reconnecting')
                await self.connect()

    async def handle_data(self, data):
        if data["topic"].startswith('channel-subscribe-events'):
            event_type = 'subscribe'
        else:
            event_type = data["topic"]
        data["message"] = json.loads(data["message"])
        payload = {
            'event_type': event_type,
            'event_source': TwitchEvent.PUBSUB,
            'event_data': data,
        }
        await database_sync_to_async(self.create_twitch_event)(payload)

    async def disconnect(self):
        await self.set_config('STATUS_WEBSOCKET', 'DISCONNECTED')
        await self.connection.close()

    async def handle_reconnect(self):
        await self.disconnect()
        await self.connect()

    async def set_config(self, key, value):
        await database_sync_to_async(setattr)(config, key, value)

    def create_twitch_event(self, payload):
        return TwitchEvent.objects.create(**payload)
