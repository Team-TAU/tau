import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token

from .utils import get_all_statuses

class TauStatusConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.group_name = 'taustatus'
        super().__init__(*args, **kwargs)

    async def connect(self):
        await self.channel_layer.group_add(
            self.group_name, self.channel_name
        )
        await self.accept()
        # data = await database_sync_to_async(get_all_statuses)()
        # await self.taustatus_event({'data': data})

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
            except Exception as err:
                print(err)
        if not self.scope['user'].id:
            self.close()

        data = await database_sync_to_async(get_all_statuses)()
        await self.taustatus_event({'data': data})

    def get_user_from_token(self, token):
        try:
            tokenObj = Token.objects.get(key=token)
            return tokenObj.user
        except Token.DoesNotExist:
            return None

    async def taustatus_event(self, event):
        if self.scope['user'].id:
            await self.send_json(event['data'])
