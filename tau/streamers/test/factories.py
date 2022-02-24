import factory
from django.db.models import signals

@factory.django.mute_signals(signals.pre_save, signals.post_save)
class StreamerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'streamers.Streamer'
        django_get_or_create = ('twitch_username', 'twitch_id',)

    id = factory.Faker('uuid4')
    twitch_username = 'TestStreamer'
    twitch_id = "54321"
    streaming = False
    disabled = False

