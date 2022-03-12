import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tau.config")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

import configurations
configurations.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.conf.urls import url
import tau.twitchevents.consumers as twitcheventsconsumers
import tau.core.consumers as coreconsumers

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                url(r'ws/worker-server/$', coreconsumers.ServerWorkerConsumer.as_asgi()),
                url(r'ws/twitch-events/$', twitcheventsconsumers.TwitchEventConsumer.as_asgi()),
                url(r'ws/tau-status/$', coreconsumers.TauStatusConsumer.as_asgi()),
                url(r'ws/irc-messages/$', coreconsumers.TwitchChatConsumer.as_asgi())
            ]
        )
    ),
})
