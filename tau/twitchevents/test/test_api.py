import datetime

import pytest
import json

from rest_framework.test import APIClient
from rest_framework import status

from tau.twitchevents.utils import generate_signature
from tau.twitchevents.serializers import TwitchEventSerializer

from tau.twitch.test.factories import TwitchEventSubSubscriptionFactory
from tau.users.test.factories import UserFactory
from tau.twitch.models import TwitchEventSubSubscription
from .factories import TwitchEventFactory
from rest_framework.authtoken.models import Token

@pytest.mark.django_db
def test_subscription_test_response():
    u = UserFactory.create()
    token = Token.objects.get(user=u)

    event_type = 'test-subscription'
    data = {
        'event': 'test',
        'data': {
            'field_1': 'value 1',
            'field_2': 'value 2'
        }
    }
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.post(
        f'/api/v1/twitch-events/{event_type}/test',
        data=data,
        format='json'
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data['event_type'] == event_type
    assert response_data['event_source'] == 'TestCall'
    assert response_data['origin'] == 'test'
    assert response_data['event_data'] == data    

@pytest.mark.django_db
def test_subscription_test_requires_auth():
    event_type = 'test-subscription'
    data = {
        'event': 'test',
        'data': {
            'field_1': 'value 1',
            'field_2': 'value 2'
        }
    }
    client = APIClient()
    response = client.post(
        f'/api/v1/twitch-events/{event_type}/test',
        data=data,
        format='json'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_subscription_setup_response(monkeypatch):
    # Generate a TwitchEventSubSubscription object to test EventSub Subscription
    # setup.
    sub_instance = TwitchEventSubSubscriptionFactory.create()
    challenge_str = 'here-is-the-challenge-string'
    dt = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    monkeypatch.setenv('TWITCH_WEBHOOK_SECRET', 'UNIT_TESTING_SECRET')
    headers = {
        'Twitch-Eventsub-Message-Id': 'abcd-1234-abcd-1234',
        'Twitch-Eventsub-Message-Timestamp': dt.isoformat()
    }
    data = {
        'challenge': challenge_str,
        'subscription': {
            'status': 'webhook_callback_verification_pending'
        }    
    }

    signature = generate_signature(headers, json.dumps(data, separators=(',', ':')))
    headers['Twitch-Eventsub-Message-Signature'] = signature

    client = APIClient()
    response = client.post(
        '/api/v1/twitch-events/test-subscription/webhook',
        data=data,
        format='json',
        HTTP_TWITCH_EVENTSUB_MESSAGE_ID='abcd-1234-abcd-1234',
        HTTP_TWITCH_EVENTSUB_MESSAGE_TIMESTAMP=dt.isoformat(),
        HTTP_TWITCH_EVENTSUB_MESSAGE_SIGNATURE=signature
    )
    response_str = response.content.decode("utf-8")
    assert response.status_code == status.HTTP_200_OK
    assert response_str == challenge_str
    sub_instance.refresh_from_db()
    assert sub_instance.status == TwitchEventSubSubscription.Statuses.CONNECTED

@pytest.mark.django_db
def test_twitch_event_replay_response():
    u = UserFactory.create()
    token = Token.objects.get(user=u)
    instance = TwitchEventFactory.create()
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    response = client.get(
        f'/api/v1/twitch-events/{instance.id}/replay',
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    serializer = TwitchEventSerializer(instance=instance)
    serialized_data = serializer.data
    serialized_data['origin'] = 'replay'
    assert data == serialized_data

@pytest.mark.django_db
def test_twitch_event_replay_requires_auth():
    instance = TwitchEventFactory.create()
    client = APIClient()
    response = client.get(
        f'/api/v1/twitch-events/{instance.id}/replay',
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
