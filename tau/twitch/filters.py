from django.db.models import Q

from django_filters import rest_framework as filters
from .models import TwitchEventSubSubscription

class TwitchEventSubSubscriptionFilter(filters.FilterSet):
    class Meta:
        model = TwitchEventSubSubscription
        fields = ('active', )
