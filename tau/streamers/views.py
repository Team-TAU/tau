from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Streamer
from .serializers import StreamerSerializer
# Create your views here.

class StreamerViewSet(viewsets.ModelViewSet):
    queryset = Streamer.objects.all()
    serializer_class = StreamerSerializer
    permission_classes = (IsAuthenticated, )
