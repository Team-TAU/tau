import factory
from django.utils.timezone import now

class TwitchEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'twitchevents.TwitchEvent'
        django_get_or_create = ('event_type', 'event_data',)

    id = factory.Faker('uuid4')
    event_id = factory.Faker('uuid4')
    event_type = 'unit_test'
    event_source = 'Test'
    event_data = factory.Sequence(lambda n: {'data': f'data {n}'})

class TwitchChannelPointRedemptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'twitchevents.TwitchEvent'
        django_get_or_create = ('event_type', 'event_data',)

    id = factory.Faker('uuid4')
    event_id = factory.Faker('uuid4')
    event_type = 'channel-channel_points_custom_reward_redemption-add'
    event_source = 'Test'
    event_data = factory.Sequence(lambda n: {'user_input': f'test input'})
