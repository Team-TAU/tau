import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token

class TwitchEventConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.group_name = 'twitchevents'
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
                    self.scope['user'] = user
            except json.JSONDecodeError as err:
                print(err)
        if not self.scope['user'].id:
            print('No user found with submitted token.  Closing connection.')
            self.close()

    async def twitchevent_event(self, event):
        if self.scope['user'].id:
            await self.send_json(event['data'])

    async def twitchevent_keepalive(self, _):
        await self.send_json({"event": "keep_alive"})

    def get_user_from_token(self, token):
        user = Token.objects.get(key=token).user
        return user
