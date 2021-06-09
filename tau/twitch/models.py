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
