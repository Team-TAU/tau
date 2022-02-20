from datetime import datetime
from django.db.models import signals
import pytest
from .factories import TwitchEventFactory

@pytest.mark.django_db
def test_twitch_event_fields():
    signals.post_save.receivers = []
    instance = TwitchEventFactory.create()
    assert type(instance.event_id) is str
    assert type(instance.event_type) is str
    assert type(instance.event_source) is str
    assert type(instance.event_data) is dict
    assert type(instance.created) is datetime
