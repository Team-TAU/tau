import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tau.config")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

# We must import configurations then immediately run configurations.setup() in order
# to properly load everything in for django
import configurations
configurations.setup()

from django.conf.urls import url
from django.urls import path
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import tau.chatbots.consumers as chatbotconsumers
import tau.core.consumers as coreconsumers
import tau.twitchevents.consumers as twitcheventsconsumers

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                url(r'ws/worker-server/$', coreconsumers.ServerWorkerConsumer.as_asgi()),
                url(r'ws/twitch-events/$', twitcheventsconsumers.TwitchEventConsumer.as_asgi()),
                url(r'ws/tau-status/$', coreconsumers.TauStatusConsumer.as_asgi()),
                url(r'ws/irc-messages/$', coreconsumers.TwitchChatConsumer.as_asgi()),
                url(r'ws/chat-bots/status/$', chatbotconsumers.ChatBotStatusConsumer.as_asgi()),
                path('ws/chat-bots/<str:chat_bot>/', chatbotconsumers.ChatBotConsumer.as_asgi(), name='chatbot'),
            ]
        )
    ),
})
