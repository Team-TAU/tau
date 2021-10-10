from django.apps import AppConfig

class TwitchConfig(AppConfig):
    name = 'tau.twitch'
    verbose_name = 'Twitch'

    def ready(self):
        try:
            import tau.twitch.signals # pylint: disable=unused-import
        except ImportError:
            pass
