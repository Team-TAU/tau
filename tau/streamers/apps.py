from django.apps import AppConfig


class StreamersConfig(AppConfig):
    name = 'tau.streamers'
    verbose_name = 'Streamers'

    def ready(self):
        try:
            import tau.streamers.signals # pylint: disable=unused-import
        except ImportError:
            pass
