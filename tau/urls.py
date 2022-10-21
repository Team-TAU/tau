from tau.chatbots.views import ChatBotChannelViewSet, ChatBotViewSet
from tau.dashboard.views import dashboard_view
from tau.core.forms import CustomAuthenticationForm
from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .core.routers import OptionalSlashRouter

from .twitch.views import (
    twitch_token_page_view,
    TwitchAPIScopeViewSet,
    TwitchHelixEndpointViewSet,
    TwitchEventSubSubcriptionsViewSet
)

from .twitchevents.views import (
    TwitchEventViewSet,
    TwitchEventModelViewSet,
)

from .streamers.views import (
    streamer_page_view,
    StreamerViewSet
)

from .core.views import (
    authenticate_bot,
    first_run_view,
    get_channel_name_view,
    process_twitch_callback_view,
    refresh_tau_token,
    refresh_token_scope,
    home_view,
    get_tau_token,
    get_public_url,
    HeartbeatViewSet,
    ServiceStatusViewSet,
    helix_view,
    irc_message_view,
    TAUSettingsViewSet,
    reset_webhooks
)

router = OptionalSlashRouter()
router.register(r'settings', TAUSettingsViewSet, basename='tau-settings')
router.register(r'chat-bots/channels', ChatBotChannelViewSet)
router.register(r'chat-bots', ChatBotViewSet)
router.register(r'twitch-events', TwitchEventViewSet, basename='twitch-events')
router.register(r'twitch-events', TwitchEventModelViewSet)
router.register(r'service-status', ServiceStatusViewSet, basename='service-status')
router.register(r'heartbeat', HeartbeatViewSet, basename='heartbeat')
router.register(r'streamers', StreamerViewSet)
router.register(r'twitch/scopes', TwitchAPIScopeViewSet)
router.register(r'twitch/helix-endpoints', TwitchHelixEndpointViewSet)
router.register(r'twitch/eventsub-subscriptions', TwitchEventSubSubcriptionsViewSet)

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
    path('api/v1/tau-user-token/', get_tau_token),
    path('api/v1/tau-user-token/refresh/', refresh_tau_token),
    path('api/v1/public_url', get_public_url),
    path('api/v1/irc', irc_message_view),
    path('api/v1/reset-webhooks', reset_webhooks),
    path('api/twitch/helix/<path:helix_path>', helix_view),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('set-channel/', get_channel_name_view),
    path('refresh-token-scope/', refresh_token_scope),
    path('twitch-callback/', process_twitch_callback_view),
    path('bot-auth/', authenticate_bot),
    path('first-run/', first_run_view),
    path('streamers/', streamer_page_view),
    path('settings/', twitch_token_page_view),
    path('dashboard', dashboard_view),
    re_path(r'^dashboard/.*$', dashboard_view),
    path('', home_view),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
