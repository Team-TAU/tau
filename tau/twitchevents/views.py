from tau.twitch.models import TwitchEventSubSubscription
import uuid

from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from constance import config

from tau.streamers.models import Streamer

from .filters import TwitchEventFilter

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
        id_ = None
        if pk != 'subscribe':
            event_id = str(uuid.uuid4())
        else:
            event_id = None
        
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
                    sub_instance = TwitchEventSubSubscription.objects.get(
                        lookup_name=pk
                    )
                    if sub_instance.subscription == None:
                        sub_instance.subscription = [data['subscription']]
                    else:
                        sub_instance.subscription.append(data['subscription'])
                    sub_instance.status = 'CON'
                    sub_instance.save()
                else:
                    streamer = Streamer.objects.get(twitch_id=data['subscription']['condition']['broadcaster_user_id'])
                    if pk == 'stream-online':
                        streamer.online_subscription = data['subscription']
                    else:
                        streamer.offline_subscription = data['subscription']
                    streamer.save()
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
                streamer_id = event['broadcaster_user_id']
                streamer = Streamer.objects.get(twitch_id=streamer_id)
                streamer.streaming = True
                streamer.save()
            elif pk == 'stream-offline':
                streamer_id = event['broadcaster_user_id']
                streamer = Streamer.objects.get(twitch_id=streamer_id)
                streamer.streaming = False
                streamer.save()

            return HttpResponse('')


class TwitchEventModelViewSet(viewsets.ModelViewSet):
    queryset = TwitchEvent.objects.all()
    serializer_class = TwitchEventSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = [DjangoFilterBackend]
    filterset_class = TwitchEventFilter

    @action(detail=True, methods=['post', 'get'])
    def replay(self, request, pk=None):
        instance = TwitchEvent.objects.get(pk=pk)
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
