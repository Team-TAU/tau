from django.http import HttpResponse
from django.template import loader

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Streamer
from .serializers import StreamerSerializer
# Create your views here.

def streamer_page_view(request):
    template = loader.get_template('streamers/streamers.html')
    return HttpResponse(template.render({}, request))


class StreamerViewSet(viewsets.ModelViewSet):
    queryset = Streamer.objects.all()
    serializer_class = StreamerSerializer
    permission_classes = (IsAuthenticated, )
