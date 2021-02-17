from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .twitchevents.views import (
    TwitchEventViewSet,
    TwitchEventModelViewSet,
)
from .core.views import (
    first_run_view,
    get_channel_name_view,
    process_twitch_callback_view,
    home_view,
    channel_point_rewards,
    get_twitch_user,
    get_tau_token,
)

router = DefaultRouter()
router.register(r'twitch-events', TwitchEventViewSet, basename='twitch-events')
router.register(r'twitch-events', TwitchEventModelViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/v1/channel-point-rewards/', channel_point_rewards),
    path('api/v1/twitch-user/', get_twitch_user),
    path('api/v1/tau-user-token/', get_tau_token),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('set-channel/', get_channel_name_view),
    path('twitch-callback/', process_twitch_callback_view),
    path('', home_view),
    path('first-run/', first_run_view),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
