from django.forms import model_to_dict
from django.db.models import signals
import pytest
from .factories import TwitchEventFactory
from ..serializers import TwitchEventSerializer


@pytest.mark.django_db
def test_serializer_with_empty_data():
    serializer = TwitchEventSerializer(data={})
    assert(not serializer.is_valid())

@pytest.mark.django_db
def test_serialzier_with_valid_data():
    signals.post_save.receivers = []
    instance = TwitchEventFactory.create()
    serializer = TwitchEventSerializer(data=model_to_dict(instance))
    assert(serializer.is_valid())

@pytest.mark.django_db
def test_serialzier_valid_keys():
    signals.post_save.receivers = []
    instance = TwitchEventFactory.create()
    serializer = TwitchEventSerializer(instance=instance)
    assert(
      sorted(list(serializer.data.keys())) == sorted([
                'id',
                'event_id',
                'event_type',
                'event_source',
                'event_data',
                'created',
                'origin'
            ])
    )
