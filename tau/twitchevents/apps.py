from django.apps import AppConfig


class TwitcheventsConfig(AppConfig):
    name = 'tau.twitchevents'
    verbose_name = 'TwitchEvents'

    def ready(self):
        try:
            import tau.twitchevents.signals # pylint: disable=unused-import
        except ImportError:
            pass
