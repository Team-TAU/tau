from django.db.models import Q

from django_filters import rest_framework as filters
from .models import TwitchEvent

class TwitchEventFilter(filters.FilterSet):
    user_id = filters.CharFilter(method='user_id_filter', label='User Id')
    user_name = filters.CharFilter(method='user_name_filter', label='User Name')
    recipient_user_id = filters.CharFilter(method='recipient_user_id_filter', label='Recipient User Id')
    recipient_user_name = filters.CharFilter(method='recipient_user_name_filter', label='Recipient User Name')
    reward_id = filters.CharFilter(method='reward_id_filter', label='Reward Id')

    def user_id_filter(self, queryset, name, value):
        return queryset.filter(
            Q(event_data__user_id__iexact=value) |
            Q(event_data__data__message__user_id__iexact=value) |
            Q(event_data__from_broadcaster_user_id__iexact=value)
        ).distinct()
    
    def user_name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(event_data__user_name__iexact=value) |
            Q(event_data__data__message__user_name__iexact=value) |
            Q(event_data__from_broadcaster_user_name__iexact=value)
        ).distinct()
    
    def recipient_user_id_filter(self, queryset, name, value):
        return queryset.filter(event_data__data__message__recipient_id__iexact=value)

    def recipient_user_name_filter(self, queryset, name, value):
        return queryset.filter(event_data__data__message__recipient_user_name__iexact=value)

    def reward_id_filter(self, queryset, name, value):
        return queryset.filter(event_data__reward__id__iexact=value)

    class Meta:
        model = TwitchEvent
        fields = (
            'event_type',
            'user_id',
            'user_name',
            'reward_id',
        )
