from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/tau-status/$', consumers.TauStatusConsumer.as_asgi()),
]