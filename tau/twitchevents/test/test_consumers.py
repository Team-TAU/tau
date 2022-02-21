import pytest
from channels.testing import WebsocketCommunicator
from tau.asgi import application
from .factories import TwitchEventFactory
from tau.twitchevents.serializers import TwitchEventSerializer
from tau.users.test.factories import UserFactory
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async

TEST_CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer",},
}

@pytest.mark.asyncio
@pytest.mark.django_db
class TestChannels:
    @database_sync_to_async
    def generate_event(self):
        instance = TwitchEventFactory.create()
        return instance

    @database_sync_to_async
    def generate_user_token(self):
        u = UserFactory.create()
        token = Token.objects.get(user=u)
        return str(token)

    async def test_sends_twitch_event(self, settings):
        token = await self.generate_user_token()
        communicator = WebsocketCommunicator(
            application=application, path='/ws/twitch-events/'
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.send_json_to({"token": token})
        instance = await self.generate_event()
        response = await communicator.receive_json_from()
        serializer = TwitchEventSerializer(instance=instance)
        assert response == serializer.data
        await communicator.disconnect()

    async def test_twitch_event_auth_required(self, settings):
        communicator = WebsocketCommunicator(
            application=application, path='/ws/twitch-events/'
        )
        connected, _ = await communicator.connect()
        assert connected
        instance = await self.generate_event()
        assert await communicator.receive_nothing() is True
        await communicator.disconnect()
