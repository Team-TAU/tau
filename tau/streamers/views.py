from django.http import HttpResponse
from django.template import loader

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import Streamer, Stream
from .serializers import StreamerSerializer, StreamSerializer
# Create your views here.

def streamer_page_view(request):
    template = loader.get_template('streamers/streamers.html')
    return HttpResponse(template.render({}, request))


class StreamerViewSet(viewsets.ModelViewSet):
    queryset = Streamer.objects.all()
    serializer_class = StreamerSerializer
    permission_classes = (IsAuthenticated, )

    @action(detail=True, methods=['get'])
    def streams(self, request, pk=None):
        streamer = self.get_object()
        streams = streamer.streams.all().order_by('-started_at')
        self.paginator.ordering = '-started_at'
        page = self.paginate_queryset(streams)
        if page is not None:
            serializer = StreamSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = StreamSerializer(streams, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'], url_path='streams/latest')
    def latest_stream(self, request, pk=None):
        streamer = self.get_object()
        try:
            stream = streamer.streams.all().latest('started_at')
            serializer = StreamSerializer(stream, many=False)
            return Response(serializer.data)
        except Stream.DoesNotExist:
            return Response({})
