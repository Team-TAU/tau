import datetime

from django.db.models import signals
import pytest
import json

from rest_framework.test import APIClient
from rest_framework import status

from tau.twitchevents.utils import generate_signature
from tau.twitch.test.factories import TwitchEventSubSubscriptionFactory
from tau.twitch.models import TwitchEventSubSubscription

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
