import pytest
from channels.testing import WebsocketCommunicator
from tau.asgi import application
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
    def generate_user_token(self):
        u = UserFactory.create()
        token = Token.objects.get(user=u)
        return str(token)

    @database_sync_to_async
    def set_constance_value(self, key, value):
        setattr(config, key, value)

    async def test_sends_on_constance_change(self, settings):
        token = await self.generate_user_token()
        communicator = WebsocketCommunicator(
            application=application, path='/ws/tau-status/'
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.send_json_to({"token": token})
        initial_response = await communicator.receive_json_from()
        await self.set_constance_value('STATUS_WEBSOCKET', 'INACTIVE')
        response = await communicator.receive_json_from()
        await communicator.disconnect()
        assert len(initial_response) == 9
        assert response == [{'event_type': 'STATUS_WEBSOCKET', 'old_value': None, 'new_value': 'INACTIVE'}]

    async def test_tau_status_auth_required(self, settings):
        communicator = WebsocketCommunicator(
            application=application, path='/ws/tau-status/'
        )
        connected, _ = await communicator.connect()
        assert connected
        await self.set_constance_value('STATUS_WEBSOCKET', 'INACTIVE')
        received_nothing = await communicator.receive_nothing() is True
        await communicator.disconnect()

        assert received_nothing

    async def test_invalid_login_data_format(self, settings):
        communicator = WebsocketCommunicator(
            application=application, path='/ws/tau-status/'
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.send_to("non-json packet")
        response = await communicator.receive_json_from()
        await self.set_constance_value('STATUS_WEBSOCKET', 'INACTIVE')
        received_nothing = await communicator.receive_nothing() is True
        await communicator.disconnect()

        assert response == {'error': 'Invalid Login'}
        assert received_nothing

    async def test_invalid_login_data_fields(self, settings):
        communicator = WebsocketCommunicator(
            application=application, path='/ws/tau-status/'
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.send_json_to({"not_a_token": "oops!"})
        response = await communicator.receive_json_from()
        await self.set_constance_value('STATUS_WEBSOCKET', 'INACTIVE')
        received_nothing = await communicator.receive_nothing() is True
        await communicator.disconnect()

        assert response == {'error': 'Missing token field'}
        assert received_nothing

    async def test_twitch_event_bad_auth(self, settings):
        token = 'Invalid Token'
        communicator = WebsocketCommunicator(
            application=application, path='/ws/tau-status/'
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.send_json_to({"token": token})
        response = await communicator.receive_json_from()
        await self.set_constance_value('STATUS_WEBSOCKET', 'INACTIVE')
        received_nothing = await communicator.receive_nothing() is True
        await communicator.disconnect()

        assert response == {'error': 'Invalid Login'}
        assert received_nothing

    async def test_resend_token(self, settings):
        token = await self.generate_user_token()
        communicator = WebsocketCommunicator(
            application=application, path='/ws/tau-status/'
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.send_json_to({"token": token})
        await communicator.send_json_to({"token": token})
        await self.set_constance_value('STATUS_WEBSOCKET', 'INACTIVE')
        response = await communicator.receive_json_from()
        await communicator.disconnect()

        assert len(response) == 9
