from django.db.models import Q

from django_filters import rest_framework as filters
from .models import TwitchEvent

class TwitchEventFilter(filters.FilterSet):
    user_id = filters.CharFilter(method='user_id_filter', label='User Id')
    user_name = filters.CharFilter(method='user_name_filter', label='User Name')
    raid_from = filters.CharFilter(method='raid_from_filter', label='Raid From')
    raid_to = filters.CharFilter(method='raid_to_filter', label='Raid To')
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

    def raid_from_filter(self, queryset, name, value):
        return queryset.filter(
            event_type='channel-raid',
            event_data__from_broadcaster_user_name__iexact=value
        )

    def raid_to_filter(self, queryset, name, value):
        return queryset.filter(
            event_type='channel-raid',
            event_data__to_broadcaster_user_name__iexact=value
        )

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
