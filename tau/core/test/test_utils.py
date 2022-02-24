from datetime import timedelta
import os
import pytest
import requests
import requests_mock
from constance import config
from django.utils import timezone
from unittest.mock import patch

from tau.core.utils import check_access_token, check_access_token_expired, cleanup_remote_webhooks, cleanup_webhooks, eventsub_payload, get_all_statuses, init_webhook, init_webhooks, log_request, refresh_access_token, setup_ngrok, streamer_payload, teardown_all_acct_webhooks, teardown_webhooks
from tau.streamers.test.factories import StreamerFactory
from tau.twitch.models import TwitchEventSubSubscription
from tau.twitch.test.factories import TwitchEventSubSubscriptionFactory


def NgrokKillMock():
    print("kill!")
    pass

class NgrokTunnelMock(object):
    pass

def NgrokConnectMock(port, bind_tls=True):
    print("connect")
    tunnel = NgrokTunnelMock()
    tunnel.public_url = 'ngrok.test.tunnel'
    return tunnel

class TestUtils():
    @pytest.mark.django_db
    def test_setup_ngrok(self, monkeypatch):
        port = 8000
        ngrok_token = "UNIT_TEST_NGROK_TOKEN"
        monkeypatch.setenv("PORT", port)
        monkeypatch.setenv("NGROK_TOKEN", ngrok_token)
        monkeypatch.setattr('pyngrok.ngrok.kill', NgrokKillMock)
        monkeypatch.setattr('pyngrok.ngrok.connect', NgrokConnectMock)
        setup_ngrok()


    @pytest.mark.django_db
    def test_check_access_token_valid(self, settings):
        access_token = "UNIT_TEST_ACCESS_TOKEN"
        config.TWITCH_ACCESS_TOKEN = access_token

        with requests_mock.Mocker() as m:
            m.get(
                'https://id.twitch.tv/oauth2/validate',
                json={
                    "client_id": "something",
                    "login": "testlogin",
                    "scopes": ["channel:scope"],
                    "user_id": "1234",
                    "expires_in": 1234567
                }
            )
            assert check_access_token()
            assert m.call_count == 1

            req = m.request_history[0]
            assert req.headers['Authorization'] == f"OAuth {access_token}"

    @pytest.mark.django_db
    def test_check_access_token_invalid(self, settings):
        with requests_mock.Mocker() as m:
            m.get(
                'https://id.twitch.tv/oauth2/validate',
                json={
                    "status": 401,
                    "message": "expired authorization token"
                }
            )
            assert not check_access_token()

    @pytest.mark.django_db
    def test_check_access_token_expired_valid(self, settings):
        expiration = timezone.now() + timedelta(hours=1)
        config.TWITCH_ACCESS_TOKEN_EXPIRATION = expiration
        assert not check_access_token_expired()

    @pytest.mark.django_db
    def test_check_access_token_expired_expired(self, settings):
        expiration = timezone.now() - timedelta(hours=1)
        config.TWITCH_ACCESS_TOKEN_EXPIRATION = expiration
        assert check_access_token_expired()

    @pytest.mark.django_db
    def test_refresh_access_token_success(self, settings):
        config.TWITCH_ACCESS_TOKEN_EXPIRATION = timezone.now() - timedelta(hours=1)
        new_access_token = 'NEW_ACCESS_TOKEN'
        new_refresh_token = 'NEW_REFRESH_TOKEN'
        expires_in = 3600
        with requests_mock.Mocker() as m:
            m.post(
                'https://id.twitch.tv/oauth2/token',
                json={
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token,
                    "expires_in": expires_in,
                    "scope": ["testing:scope:1", "testing:scope:2"],
                    "token_type": "bearer"
                }
            )
            refresh_access_token()
        
        assert config.TWITCH_ACCESS_TOKEN == new_access_token
        assert config.TWITCH_REFRESH_TOKEN == new_refresh_token
        assert not check_access_token_expired()

    @pytest.mark.django_db
    def test_refresh_access_token_invalid(self, settings):
        config.TWITCH_ACCESS_TOKEN_EXPIRATION = timezone.now() - timedelta(hours=1)
        with requests_mock.Mocker() as m:
            m.post(
                'https://id.twitch.tv/oauth2/token',
                json={
                    "error": "Bad Request",
                    "status": 400,
                    "message": "Invalid refresh token"
                }
            )
            refresh_access_token()
        
        assert check_access_token_expired()

    @pytest.mark.django_db
    def test_get_all_statuses(self, settings):
        init_statuses = [
           {'event_type': 'STATUS_WEBSOCKET', 'old_value': None, 'new_value': 'INACTIVE'},
           {'event_type': 'STATUS_CHANNEL_UPDATE', 'old_value': None, 'new_value': 'INACTIVE'},
           {'event_type': 'STATUS_CHANNEL_FOLLOW', 'old_value': None, 'new_value': 'INACTIVE'},
           {'event_type': 'STATUS_CHANNEL_CHEER', 'old_value': None, 'new_value': 'INACTIVE'},
           {'event_type': 'STATUS_CHANNEL_POINT_REDEMPTION', 'old_value': None, 'new_value': 'INACTIVE'},
           {'event_type': 'STATUS_CHANNEL_RAID', 'old_value': None, 'new_value': 'INACTIVE'},
           {'event_type': 'STATUS_CHANNEL_HYPE_TRAIN_BEGIN', 'old_value': None, 'new_value': 'INACTIVE'},
           {'event_type': 'STATUS_CHANNEL_HYPE_TRAIN_PROGRESS', 'old_value': None, 'new_value': 'INACTIVE'},
           {'event_type': 'STATUS_CHANNEL_HYPE_TRAIN_END', 'old_value': None, 'new_value': 'INACTIVE'} 
        ]
        assert sorted(get_all_statuses(), key=lambda x: x['event_type']) == sorted(init_statuses, key=lambda x: x['event_type'])

    @pytest.mark.django_db
    def test_log_reqest(self, settings, capsys):
        with requests_mock.Mocker() as m:
            url = 'https://testurl.com'
            status_code = 200
            m.get(url, status_code=status_code, json={
                "str_data": "sample string",
                "list_data": ["sample 1", "sample 2"],
                "obj_data": {
                    "label1": "value1",
                    "label2": "value2"
                }
            })
            req = requests.get(url)
            log_request(req)
        captured = capsys.readouterr()
        assert '[REQUEST]' in captured.out

    @pytest.mark.django_db
    def test_eventsub_payload(self, settings, monkeypatch):
        instance = TwitchEventSubSubscriptionFactory.create()
        base_url = 'https://test.url'
        config.CHANNEL_ID="123456"
        monkeypatch.setenv('TWITCH_WEBHOOK_SECRET', 'UNIT_TESTING_SECRET')
        expected_payload = {
            'type': instance.name,
            'version': instance.version,
            'condition': {'broadcaster_user_id': config.CHANNEL_ID}, 
            'transport': {
                'method': 'webhook',
                'callback': f'{base_url}/api/v1/twitch-events/{instance.lookup_name}/webhook/',
                'secret': os.environ.get('TWITCH_WEBHOOK_SECRET', None)
            }
        }

        payload = eventsub_payload(instance, base_url)
        assert payload == expected_payload

    @pytest.mark.django_db
    def test_streamer_payload(self, settings, monkeypatch):
        base_url = 'https://test.url'
        status = 'online'
        streamer_id = '1234'
        monkeypatch.setenv('TWITCH_WEBHOOK_SECRET', 'UNIT_TESTING_SECRET')
        expected_payload = {
            'type': f'stream.{status}',
            'version': "1",
            "condition": {
                'broadcaster_user_id': streamer_id
            },
            'transport': {
                'method': 'webhook',
                'callback': f'{base_url}/api/v1/twitch-events/stream-{status}/webhook/',
                'secret': os.environ.get('TWITCH_WEBHOOK_SECRET', None)
            }
        }

        payload = streamer_payload(base_url, status, streamer_id)
        assert payload == expected_payload

    @pytest.mark.django_db
    def test_init_webhook_instance(self, settings, monkeypatch):
        base_url = 'https://test.url'
        config.CHANNEL_ID="123456"
        monkeypatch.setenv('TWITCH_WEBHOOK_SECRET', 'UNIT_TESTING_SECRET')
        worker_token = 'WORKER_TOKEN'

        instance = TwitchEventSubSubscriptionFactory.create()
        payload = eventsub_payload(instance, base_url)
        with requests_mock.Mocker() as m:
            m.patch(f'{base_url}/api/v1/twitch/eventsub-subscriptions/{instance.lookup_name}', json={"response": "test success"})
            m.post('https://api.twitch.tv/helix/eventsub/subscriptions', json={"response": "test success"})
            init_webhook(payload, url=base_url, worker_token=worker_token, instance_id=instance.lookup_name)
            assert m.call_count == 2
            history = m.request_history
            assert history[0].method == 'PATCH'
            assert history[0].text == 'status=CTG'
            assert history[0].url == f'{base_url}/api/v1/twitch/eventsub-subscriptions/{instance.lookup_name}'
            assert history[1].method == 'POST'
            assert history[1].json() == payload
            assert history[1].url == 'https://api.twitch.tv/helix/eventsub/subscriptions'

    @pytest.mark.django_db
    def test_init_webhook_no_instance(self, settings, monkeypatch):
        base_url = 'https://test.url'
        config.CHANNEL_ID="123456"
        monkeypatch.setenv('TWITCH_WEBHOOK_SECRET', 'UNIT_TESTING_SECRET')
        worker_token = 'WORKER_TOKEN'

        payload = streamer_payload(base_url, 'online', '12345')

        with requests_mock.Mocker() as m:
            m.post('https://api.twitch.tv/helix/eventsub/subscriptions', json={"response": "test success"})
            init_webhook(payload, url=base_url, worker_token=worker_token)
            assert m.call_count == 1
            history = m.request_history
            assert history[0].method == 'POST'
            assert history[0].json() == payload
            assert history[0].url == 'https://api.twitch.tv/helix/eventsub/subscriptions'

    @pytest.mark.django_db
    def test_init_webhooks(self, settings, monkeypatch):
        base_url = 'https://test.url'
        settings.LOCAL_URL = base_url
        TwitchEventSubSubscriptionFactory.create(
            name='channel.raid',
            lookup_name='channel-raid',
            subscription_type='Channel Raid'
        )
        TwitchEventSubSubscriptionFactory.create(
            name='channel.update',
            lookup_name='channel-update',
            subscription_type='Channel Update'
        )
        StreamerFactory.create()
        config.CHANNEL_ID = '123456'
        monkeypatch.setenv('TWITCH_WEBHOOK_SECRET', 'UNIT_TESTING_SECRET')
        worker_token = 'WORKER_TOKEN'
        with requests_mock.Mocker() as m:
            for instance in TwitchEventSubSubscription.objects.all():
                m.patch(f'{base_url}/api/v1/twitch/eventsub-subscriptions/{instance.lookup_name}', json={"response": "test success"})
            m.post('https://api.twitch.tv/helix/eventsub/subscriptions', json={"response": "test success"})
            init_webhooks(base_url, worker_token)
            assert m.call_count == 6

    @pytest.mark.django_db
    def test_teardown_webhooks(self, settings, monkeypatch):
        base_url = 'https://test.url'
        settings.LOCAL_URL = base_url
        config.TWITCH_APP_ACCESS_TOKEN = 'UNIT_TESTING_TWITCH_ACCESS_TOKEN'
        monkeypatch.setenv('TWITCH_APP_ID', 'UNIT_TESTING_TWITCH_APP_ID')
        worker_token = 'WORKER_TOKEN'

        TwitchEventSubSubscriptionFactory.create(
            name='channel.raid',
            lookup_name='channel-raid',
            subscription_type='Channel Raid'
        )
        TwitchEventSubSubscriptionFactory.create(
            name='channel.update',
            lookup_name='channel-update',
            subscription_type='Channel Update'
        )

        # Create an inactive subscription- an attempt to disconnect
        # this webhook should not occur.
        TwitchEventSubSubscriptionFactory.create(
            name='test.inactive',
            lookup_name='test-inactive',
            subscription_type='Test Inactive',
            subscription=None
        )

        StreamerFactory.create(
            online_subscription={'id': 'STREAMER_ONLINE_ID'},
            offline_subscription={'id': 'STREAMER_OFFLINE_ID'}
        )

        # Create an inactive streamer- an attempt to disconnect
        # this webhook should not occur.
        StreamerFactory.create(
            online_subscription=None,
            offline_subscription=None
        )
        
        # Create an inactive streamer- an attempt to disconnect
        # this webhook should not occur.
        StreamerFactory.create()

        with requests_mock.Mocker() as m:
            m.delete(f'https://api.twitch.tv/helix/eventsub/subscriptions')
            for sub in TwitchEventSubSubscription.objects.all():
                m.patch(
                    f'{base_url}/api/v1/twitch/eventsub-subscriptions/{sub.lookup_name}',
                    json={"response": "test success"}
                )
            teardown_webhooks(worker_token)
            assert m.call_count == 6
            for req in m.request_history:
                if req.hostname == 'api.twitch.tv':
                    assert req.headers['Client-ID'] == 'UNIT_TESTING_TWITCH_APP_ID'
                    assert req.headers['Authorization'] == f'Bearer UNIT_TESTING_TWITCH_ACCESS_TOKEN'
                else:
                    assert req.headers['Authorization'] == 'Token WORKER_TOKEN'

    @pytest.mark.django_db
    def test_cleanup_webhooks(self, settings, monkeypatch):
        config.TWITCH_APP_ACCESS_TOKEN = 'UNIT_TESTING_TWITCH_ACCESS_TOKEN'
        monkeypatch.setenv('TWITCH_APP_ID', 'UNIT_TESTING_TWITCH_APP_ID')
        with requests_mock.Mocker() as m:
            m.get(f'https://api.twitch.tv/helix/eventsub/subscriptions', json={
                    'data': [
                        {'status': 'enabled', 'id': 'SHOULD_NOT_DELETE_ID'},
                        {'status': 'webhook_callback_verification_pending', 'id': 'SHOULD_DELETE_ID'},
                        {'status': 'webhook_callback_verification_failed', 'id': 'SHOULD_DELETE_ID'},
                        {'status': 'notification_failures_exceeded', 'id': 'SHOULD_DELETE_ID'},
                        {'status': 'authorization_revoked', 'id': 'SHOULD_DELETE_ID'},
                        {'status': 'user_removed', 'id': 'SHOULD_DELETE_ID'},
                    ]
                }
            )
            m.delete(f'https://api.twitch.tv/helix/eventsub/subscriptions')
            cleanup_webhooks()
            assert m.call_count == 6
            for req in filter(lambda x: x.method == 'DELETE',m.request_history):
                assert req.headers['Client-ID'] == 'UNIT_TESTING_TWITCH_APP_ID'
                assert req.headers['Authorization'] == f'Bearer UNIT_TESTING_TWITCH_ACCESS_TOKEN'
                assert req.qs['id'][0].upper() == 'SHOULD_DELETE_ID'

    @pytest.mark.django_db
    def test_cleanup_remote_webhooks(self, settings, monkeypatch):
        config.TWITCH_APP_ACCESS_TOKEN = 'UNIT_TESTING_TWITCH_ACCESS_TOKEN'
        monkeypatch.setenv('TWITCH_APP_ID', 'UNIT_TESTING_TWITCH_APP_ID')
        config.PUBLIC_URL='https://local.url/'
        with requests_mock.Mocker() as m:
            m.get(f'https://api.twitch.tv/helix/eventsub/subscriptions', json={
                    'data': [
                        {'id': 'SHOULD_NOT_DELETE_ID', 'transport': {'callback': 'https://local.url/some/endpoint'}},
                        {'id': 'SHOULD_DELETE_ID', 'transport': {'callback': 'https://remote.url/some/endpoint'}},
                        {'id': 'SHOULD_NOT_DELETE_ID', 'transport': {'callback': 'https://local.url/some/other/endpoint'}},
                        {'id': 'SHOULD_DELETE_ID', 'transport': {'callback': 'https://remote.url/some/other/endpoint'}},
                        {'id': 'SHOULD_DELETE_ID', 'transport': {'callback': 'https://local.url:8000/some/other/endpoint'}},
                        {'id': 'SHOULD_NOT_DELETE_ID', 'transport': {'callback': 'http://local.url/some/other/endpoint'}},
                    ]
                }
            )
            m.delete(f'https://api.twitch.tv/helix/eventsub/subscriptions')
            cleanup_remote_webhooks()
            assert m.call_count == 4
            for req in filter(lambda x: x.method == 'DELETE',m.request_history):
                assert req.headers['Client-ID'] == 'UNIT_TESTING_TWITCH_APP_ID'
                assert req.headers['Authorization'] == f'Bearer UNIT_TESTING_TWITCH_ACCESS_TOKEN'
                assert req.qs['id'][0].upper() == 'SHOULD_DELETE_ID'

    @pytest.mark.django_db
    def test_teardown_all_acct_webhooks(self, settings, monkeypatch):
        config.TWITCH_APP_ACCESS_TOKEN = 'UNIT_TESTING_TWITCH_ACCESS_TOKEN'
        monkeypatch.setenv('TWITCH_APP_ID', 'UNIT_TESTING_TWITCH_APP_ID')
        config.PUBLIC_URL='https://local.url/'
        with requests_mock.Mocker() as m:
            m.get(f'https://api.twitch.tv/helix/eventsub/subscriptions', json={
                    'data': [
                        {'id': 'SHOULD_DELETE_ID', 'status': 'enabled', 'transport': {'callback': 'https://local.url/some/endpoint'}},
                        {'id': 'SHOULD_DELETE_ID', 'status': 'webhook_callback_verification_pending', 'transport': {'callback': 'https://remote.url/some/endpoint'}},
                        {'id': 'SHOULD_DELETE_ID', 'status': 'webhook_callback_verification_failed', 'transport': {'callback': 'https://local.url/some/other/endpoint'}},
                        {'id': 'SHOULD_DELETE_ID', 'status': 'notification_failures_exceeded', 'transport': {'callback': 'https://remote.url/some/other/endpoint'}},
                        {'id': 'SHOULD_DELETE_ID', 'status': 'authorization_revoked', 'transport': {'callback': 'https://local.url:8000/some/other/endpoint'}},
                        {'id': 'SHOULD_DELETE_ID', 'status': 'user_removed', 'transport': {'callback': 'http://local.url/some/other/endpoint'}},
                    ]
                }
            )
            m.delete(f'https://api.twitch.tv/helix/eventsub/subscriptions')
            teardown_all_acct_webhooks()
            assert m.call_count == 7
            for req in filter(lambda x: x.method == 'DELETE',m.request_history):
                assert req.headers['Client-ID'] == 'UNIT_TESTING_TWITCH_APP_ID'
                assert req.headers['Authorization'] == f'Bearer UNIT_TESTING_TWITCH_ACCESS_TOKEN'
                assert req.qs['id'][0].upper() == 'SHOULD_DELETE_ID'
