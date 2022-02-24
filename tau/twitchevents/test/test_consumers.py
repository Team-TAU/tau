import pytest
from channels.testing import WebsocketCommunicator
from tau.asgi import application
from .factories import TwitchEventFactory, TwitchChannelPointRedemptionFactory
from tau.twitchevents.serializers import TwitchEventSerializer
from tau.users.test.factories import UserFactory
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from constance import config

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
    def generate_channel_point_redemption(self):
        instance = TwitchChannelPointRedemptionFactory.create()
        return instance

    @database_sync_to_async
    def generate_user_token(self):
        u = UserFactory.create()
        token = Token.objects.get(user=u)
        return str(token)

    @database_sync_to_async
    def set_constance_value(self, key, value):
        setattr(config, key, value)

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
        await communicator.disconnect()

        assert response == serializer.data

    async def test_channel_points_dont_send_with_irc_enabled(self, settings):
        await self.set_constance_value('USE_IRC', True)
        token = await self.generate_user_token()
        communicator = WebsocketCommunicator(
            application=application, path='/ws/twitch-events/'
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.send_json_to({"token": token})
        instance = await self.generate_channel_point_redemption()
        received_nothing = await communicator.receive_nothing() is True
        await communicator.disconnect()

        assert received_nothing

    async def test_twitch_event_auth_required(self, settings):
        communicator = WebsocketCommunicator(
            application=application, path='/ws/twitch-events/'
        )
        connected, _ = await communicator.connect()
        assert connected
        instance = await self.generate_event()
        received_nothing = await communicator.receive_nothing() is True
        await communicator.disconnect()

        assert received_nothing

    async def test_invalid_login_data_format(self, settings):
        communicator = WebsocketCommunicator(
            application=application, path='/ws/twitch-events/'
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.send_to("non-json packet")
        response = await communicator.receive_json_from()
        instance = await self.generate_event()
        received_nothing = await communicator.receive_nothing() is True
        await communicator.disconnect()

        assert response == {'error': 'Invalid Login'}
        assert received_nothing

    async def test_invalid_login_data_fields(self, settings):
        communicator = WebsocketCommunicator(
            application=application, path='/ws/twitch-events/'
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.send_json_to({"not_a_token": "oops!"})
        response = await communicator.receive_json_from()
        instance = await self.generate_event()
        received_nothing = await communicator.receive_nothing() is True
        await communicator.disconnect()

        assert response == {'error': 'Missing token field'}
        assert received_nothing

    async def test_twitch_event_bad_auth(self, settings):
        token = 'Invalid Token'
        communicator = WebsocketCommunicator(
            application=application, path='/ws/twitch-events/'
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.send_json_to({"token": token})
        response = await communicator.receive_json_from()
        instance = await self.generate_event()
        received_nothing = await communicator.receive_nothing() is True
        await communicator.disconnect()

        assert response == {'error': 'Invalid Login'}
        assert received_nothing

    async def test_resend_token(self, settings):
        token = await self.generate_user_token()
        communicator = WebsocketCommunicator(
            application=application, path='/ws/twitch-events/'
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.send_json_to({"token": token})
        await communicator.send_json_to({"token": token})
        instance = await self.generate_event()
        response = await communicator.receive_json_from()
        serializer = TwitchEventSerializer(instance=instance)
        await communicator.disconnect()

        assert response == serializer.data
