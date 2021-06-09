from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import TwitchAPIScope, TwitchHelixEndpoint
from .serializers import TwitchAPIScopeSerializer, TwitchEndpointSerializer

# Create your views here.
def twitch_token_page_view(request):
    template = loader.get_template('twitch/twitch_token_scopes.html')
    return HttpResponse(template.render({}, request))

class TwitchHelixEndpointViewSet(viewsets.ModelViewSet):
    queryset = TwitchHelixEndpoint.objects.all()
    serializer_class = TwitchEndpointSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = None

class TwitchAPIScopeViewSet(viewsets.ModelViewSet):
    queryset = TwitchAPIScope.objects.all()
    serializer_class = TwitchAPIScopeSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = None
    
    @action(methods=['PUT'], detail=False, url_path='bulk')
    def bulk(self, request):
        data = request.data
        ids = [row['id'] for row in data]
        for inst_data in data:
            instance = TwitchAPIScope.objects.get(pk=inst_data['id'])
            serializer = self.get_serializer(instance, data=inst_data, partial=False)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

        instances = TwitchAPIScope.objects.filter(id__in=ids)
        serializer = self.get_serializer(instances, many=True)

        return Response(serializer.data)
