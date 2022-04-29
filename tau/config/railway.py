import os
from .common import Common
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Railway(Common):
    PUBLIC_URL = os.environ.get("RAILWAY_STATIC_URL")
    PROTOCOL = "https:"
    BASE_PORT = 443
    BASE_URL = f"{PROTOCOL}//{PUBLIC_URL}"
    USE_NGROK = False
    LOCAL_URL = BASE_URL

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [
                    os.environ.get("REDIS_URL")
                ],
            },
        },
    }

    DEBUG = os.environ.get('DEBUG', "False").lower() == "true"

    ins = list(Common.MIDDLEWARE).index('django.middleware.security.SecurityMiddleware')
    if ins:
        MIDDLEWARE=list(Common.MIDDLEWARE)
        MIDDLEWARE.insert(ins+1, 'whitenoise.middleware.WhiteNoiseMiddleware')
        MIDDLEWARE=tuple(MIDDLEWARE)
    
    ALLOWED_HOSTS = ["*"]

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.getenv('DJANGO_DB', 'tau_db'),
            'USER': os.getenv('DJANGO_DB_USER', 'tau_db'),
            'PASSWORD': os.getenv('DJANGO_DB_PW'),
            'HOST': os.getenv('PGHOST'),
            'PORT': os.getenv('PGPORT'),
        }
    }
