import uuid

from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from constance import config

from tau.streamers.models import Streamer

from .models import (
    TwitchEvent
)
from .serializers import (
    TwitchEventSerializer,
)
from .utils import valid_webhook_request

class TwitchEventViewSet(viewsets.ViewSet):
    """
    Viewset for twitch events
    """
    permission_classes = (AllowAny,)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        event_data = request.data
        id_ = str(uuid.uuid4())
        event_id = str(uuid.uuid4())
        ws_payload = {
            'id': id_,
            'event_id': event_id,
            'event_type': pk,
            'event_source': 'TestCall',
            'event_data': event_data,
            'created': timezone.now().isoformat(),
            'origin': 'test'
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('twitchevents', {
            'type': 'twitchevent.event',
            'data': ws_payload
        })
        return Response(ws_payload)

    @action(detail=True, methods=['post'])
    def webhook(self, request, pk=None):
        body = request.body.decode('utf-8')
        data = request.data
        headers = request.headers
        status = data['subscription']['status']
        if status == 'webhook_callback_verification_pending':
            if valid_webhook_request(headers, body):
                if pk not in ['stream-offline', 'stream-online']:
                    status_key = f'STATUS_CHANNEL_{pk.upper().replace("-", "_")}'
                    setattr(config, status_key, 'CONNECTED')
                return HttpResponse(data['challenge'])
            else:
                return HttpResponseForbidden()
        else:
            event = data['event']
            event_id = headers['Twitch-Eventsub-Message-Id']
            if TwitchEvent.objects.filter(event_id=event_id).exists():
                return HttpResponse('')

            TwitchEvent.objects.create(
                event_id=event_id,
                event_type=pk,
                event_source=TwitchEvent.EVENTSUB,
                event_data=event
            )
            if pk == 'stream-online':
                streamer_username = event['broadcaster_user_login']
                streamer = Streamer.objects.get(twitch_username=streamer_username)
                streamer.streaming = True
                streamer.save()
            elif pk == 'stream-offline':
                streamer_username = event['broadcaster_user_login']
                streamer = Streamer.objects.get(twitch_username=streamer_username)
                streamer.streaming = False
                streamer.save()

            return HttpResponse('')


class TwitchEventModelViewSet(viewsets.ModelViewSet):
    queryset = TwitchEvent.objects.all()
    serializer_class = TwitchEventSerializer
    permission_classes = (IsAuthenticated, )

    @action(detail=True, methods=['post'])
    def replay(self, request, pk=None):
        instance = self.get_object()
        serializer = TwitchEventSerializer(instance, many=False)
        ws_payload = serializer.data
        ws_payload['origin'] = 'replay'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('twitchevents', {
            'type': 'twitchevent.event',
            'data': ws_payload
        })
        return Response(ws_payload)
