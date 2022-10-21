from django.apps import AppConfig

class ChatBotsConfig(AppConfig):
    name = 'tau.chatbots'
    verbose_name = 'ChatBots'

    def ready(self):
        try:
            import tau.chatbots.signals # pylint: disable=unused-import
        except ImportError:
            pass
