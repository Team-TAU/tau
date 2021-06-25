import os
from .common import Common


class Production(Common):
    INSTALLED_APPS = Common.INSTALLED_APPS

    DEBUG = os.environ.get('DEBUG', "False").lower() == "true"

    ins = list(Common.MIDDLEWARE).index('django.middleware.security.SecurityMiddleware')
    if ins:
        MIDDLEWARE=list(Common.MIDDLEWARE)
        MIDDLEWARE.insert(ins+1, 'whitenoise.middleware.WhiteNoiseMiddleware')
        MIDDLEWARE=tuple(MIDDLEWARE)
    
    # Site
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]
    