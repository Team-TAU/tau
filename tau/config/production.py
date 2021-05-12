import os
from .common import Common


class Production(Common):
    INSTALLED_APPS = Common.INSTALLED_APPS

    # Site
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]
    