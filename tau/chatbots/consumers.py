import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from constance import config

from rest_framework.authtoken.models import Token

from .models import ChatBot

class ChatBotConsumer(AsyncJsonWebsocketConsumer):
    chat_bot = None
    chat_bot_name = ''
    group_name = ''
    subscribed = False
    streamer = False

    async def connect(self):
        self.chat_bot_name = self.scope['url_route']['kwargs']['chat_bot']
        try:
            streamer = await database_sync_to_async(self.get_streamer)()
            if streamer != self.chat_bot_name:
                await database_sync_to_async(self.get_bot)()
            else:
                self.streamer = True
        except ChatBot.DoesNotExist:
            await self.close()

        self.group_name = f'chat_bot__{self.chat_bot_name}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    def get_bot(self):
        self.chat_bot = ChatBot.objects.get(user_login__iexact=self.chat_bot_name)

    def get_streamer(self):
        return config.CHANNEL.lower()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        if self.subscribed and not self.streamer:
            await self.subscription('unsubscribe')

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if self.scope['user'].id:
            # pass message to be posted to twitch chat
            # channel_layer = get_channel_layer()
            data = json.loads(text_data)
            irc_channel = data.get("irc_channel", "")
            message = data.get("message", "")
            await self.channel_layer.group_send(
                'serverworker',
                {
                    'type': 'serverworker.event',
                    'data': {
                        'action': 'irc-send',
                        'irc_username': self.chat_bot_name,
                        'irc_channel': irc_channel,
                        'message': message
                    }
                }
            )
        else:
            try:
                data = json.loads(text_data)
                if 'token' in data.keys():
                    token = data['token']
                    user = await database_sync_to_async(self.get_user_from_token)(token)
                    if user is not None:
                        self.scope['user'] = user
                        await self.subscription('subscribe')
            except json.JSONDecodeError as err:
                print(err)
        if not self.scope['user'].id:
            await self.send_json({'error': 'the provided token does not match any users.'})
            self.close()

    async def subscription(self, action):
        self.subscribed = action == 'subscribe'
        await self.channel_layer.group_send(
            'serverworker',
            {
                'type': 'serverworker.event',
                'data': {
                    'action': f'irc-{action}',
                    'irc_username': self.chat_bot_name,
                }
            }
        )

    async def chatbot_event(self, event):
        await self.send_json(event['data'])

    async def chatbot_keepalive(self, _):
        await self.send_json({"event": "keep_alive"})

    def get_user_from_token(self, token):
        user = Token.objects.get(key=token).user
        return user


class ChatBotStatusConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.group_name = 'chatbotstatus'
        super().__init__(*args, **kwargs)

    async def connect(self):
        await self.channel_layer.group_add(
            self.group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name, self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if self.scope['user'].id:
            pass
        else:
            try:
                data = json.loads(text_data)
                if 'token' in data.keys():
                    token = data['token']
                    user = await database_sync_to_async(self.get_user_from_token)(token)
                    if user is not None:
                        self.scope['user'] = user
            except json.JSONDecodeError as err:
                print(err)
        if not self.scope['user'].id:
            await self.send_json({'error': 'the provided token does not match any users.'})
            self.close()

    async def chatbotstatus_event(self, event):
        await self.send_json(event['data'])

    async def chatbotstatus_keepalive(self, _):
        await self.send_json({"event": "keep_alive"})

    def get_user_from_token(self, token):
        user = Token.objects.get(key=token).user
        return user
