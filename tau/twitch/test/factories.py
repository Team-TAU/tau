import factory


class TwitchEventSubSubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'twitch.TwitchEventSubSubscription'
        django_get_or_create = ('name', 'lookup_name', 'subscription_type', 'event_schema', 'condition_schema')

    id = factory.Faker('uuid4')
    name = 'test.subscription'
    lookup_name = 'test-subscription'
    subscription_type = 'Test Subscription'
    description = 'A subscription for unit testing'
    active = True
    version = '1'
    scope_required = 'test:subscription'
    status = 'DIS'
    subscription = {'description': 'test-subscription data', 'id': 'SUBSCRIPTION_ID'}
    event_schema = {'description': 'schema for test-subscription'}
    condition_schema = {'description': 'conditions for setting up subscription'}
