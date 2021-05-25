from tau.core.forms import CustomAuthenticationForm
from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .twitchevents.views import (
    TwitchEventViewSet,
    TwitchEventModelViewSet,
)

from .streamers.views import (
    streamer_page_view,
    StreamerViewSet
)

from .core.views import (
    first_run_view,
    get_channel_name_view,
    get_streams,
    process_twitch_callback_view,
    refresh_token_scope,
    home_view,
    channel_point_rewards,
    get_twitch_user,
    get_tau_token,
    HeartbeatViewSet,
    ServiceStatusViewSet,
)

router = DefaultRouter()
router.register(r'twitch-events', TwitchEventViewSet, basename='twitch-events')
router.register(r'twitch-events', TwitchEventModelViewSet)
router.register(r'service-status', ServiceStatusViewSet, basename='service-status')
router.register(r'heartbeat', HeartbeatViewSet, basename='heartbeat')
router.register(r'streamers', StreamerViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', 
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            authentication_form=CustomAuthenticationForm
        ),
        name='login'
    ),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/v1/channel-point-rewards/', channel_point_rewards),
    path('api/v1/twitch-user/', get_twitch_user),
    path('api/v1/tau-user-token/', get_tau_token),
    path('api/v1/helix/streams/', get_streams),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('set-channel/', get_channel_name_view),
    path('refresh-token-scope/', refresh_token_scope),
    path('twitch-callback/', process_twitch_callback_view),
    path('first-run/', first_run_view),
    path('streamers/', streamer_page_view),
    path('', home_view),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
