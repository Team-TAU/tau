import uuid

from django.utils.translation import gettext_lazy as _
from django.db import models

# Create your models here.
class TwitchAPIScope(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scope = models.CharField(max_length=255)
    required = models.BooleanField(default=False)

    class Meta:
        ordering = ['scope']

class TwitchHelixEndpoint(models.Model):
    class TokenTypes(models.TextChoices):
        OATH = 'OA', _('OAuth User Token')
        APP = 'AP', _('App Access Token')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=255)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=16)
    reference_url = models.CharField(max_length=255)
    token_type = models.CharField(max_length=2, choices=TokenTypes.choices)
    scope = models.ForeignKey(
        TwitchAPIScope,
        on_delete=models.PROTECT,
        related_name='endpoints',
        null=True,
        blank=True
    )


class TwitchEventSubSubscription(models.Model):
    class Statuses(models.TextChoices):
        DISCONNECTED = 'DIS', _('Disconnected')
        CONNECTING = 'CTG', _('Connecting')
        CONNECTED = 'CON', _('Connected')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    lookup_name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    subscription_type = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)
    version = models.CharField(max_length=16)
    scope_required = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=3, choices=Statuses.choices, blank=True, null=True)
    base_url = models.CharField(max_length=255, blank=True, null=True)
    subscription = models.JSONField(blank=True, null=True)
    event_schema = models.JSONField()
    condition_schema = models.JSONField()

    class Meta:
        ordering = ('name', )
