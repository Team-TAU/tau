import os
import sys
from os.path import join
from distutils.util import strtobool
from configurations import Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime


class Common(Configuration):  # pylint: disable=no-init
    PUBLIC_URL = os.environ.get("PUBLIC_URL", "localhost")
    PROTOCOL = os.environ.get("PROTOCOL", "http:")
    BASE_PORT = int(os.environ.get("PORT", 8000))
    BASE_URL = f"{PROTOCOL}//{PUBLIC_URL}"
    BEHIND_PROXY = (os.environ.get("BEHIND_PROXY", "false").lower() == "true")
    BASE_DIR = BASE_DIR

    if BASE_PORT not in [80, 443] and not BEHIND_PROXY:
        BASE_URL = BASE_URL + f":{BASE_PORT}"

    IS_SERVER = len(sys.argv) > 1 and "shell" not in sys.argv
    DEV_SERVER = len(sys.argv) > 1 and sys.argv[1] == "runserver"

    USE_NGROK = (os.environ.get("USE_NGROK", "False") == "True" and
                    os.environ.get("RUN_MAIN", None) != "true")

    if USE_NGROK:
        LOCAL_URL = f"http://localhost:{BASE_PORT}"
    else:
        LOCAL_URL = BASE_URL

    DEBUG_TWITCH_CALLS = os.environ.get("DEBUG_TWITCH_CALLS", "False").lower() == "true"

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'constance.backends.database',
        'django_extensions',
        'corsheaders',

        # Third party apps
        'channels',                  # websockets
        'rest_framework',            # utilities for rest apis
        'rest_framework.authtoken',  # token authentication
        'django_filters',            # for filtering rest endpoints

        # Your apps
        'tau.users',
        'tau.core.apps.CoreConfig',
        'tau.twitch.apps.TwitchConfig',
        'tau.twitchevents.apps.TwitcheventsConfig',
        'tau.streamers.apps.StreamersConfig',
        'tau.dashboard.apps.DashboardConfig'
    )

    # https://docs.djangoproject.com/en/2.0/topics/http/middleware/
    MIDDLEWARE = (
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

    ALLOWED_HOSTS = ["*"]
    CORS_ALLOW_ALL_ORIGINS = True
    ROOT_URLCONF = 'tau.urls'
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
    WSGI_APPLICATION = 'tau.wsgi.application'
    ASGI_APPLICATION = 'tau.asgi.application'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    REDIS_ENDPOINT = os.environ.get('REDIS_ENDPOINT','redis:6379')
    REDIS_PW = os.environ.get('REDIS_PW','')

    if REDIS_PW != '':
        REDIS_SERVER = f'redis://:{REDIS_PW}@{REDIS_ENDPOINT}'
    else:
        REDIS_SERVER = f'redis://{REDIS_ENDPOINT}'

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [REDIS_SERVER],
            },
        },
    }

    # Email
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    ADMINS = (
        ('Author', 'finitesingularityttv@gmail.com'),
    )

    DB_TYPE = os.environ.get('DJANGO_DB_TYPE', 'postgres')

    # Postgres
    if DB_TYPE == 'postgres':
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': os.getenv('DJANGO_DB', 'tau_db'),
                'USER': os.getenv('DJANGO_DB_USER', 'tau_db'),
                'PASSWORD': os.getenv('DJANGO_DB_PW'),
                'HOST': os.getenv('DJANGO_DB_HOST', 'db'),
                'PORT': os.getenv('DJANGO_DB_PORT', 5432),
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db/data/db.sqlite3',
                'USER': '',
                'PASSWORD': '',
                'HOST': '',
                'PORT': '',
            }
        }

    # General
    APPEND_SLASH = False
    TIME_ZONE = 'UTC'
    LANGUAGE_CODE = 'en-us'
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_L10N = True
    USE_TZ = True
    LOGIN_REDIRECT_URL = '/'
    LOGOUT_REDIRECT_URL = '/'

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), 'static'))
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'templates/static')
    ]
    STATIC_URL = '/static/'
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )
    # Media files
    MEDIA_ROOT = join(os.path.dirname(BASE_DIR), 'media')
    MEDIA_URL = '/media/'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['{}/templates'.format(BASE_DIR)],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'constance.context_processors.config',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = strtobool(os.getenv('DJANGO_DEBUG', 'no'))

    # Password Validation
    # https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'django.server': {
                '()': 'django.utils.log.ServerFormatter',
                'format': '[%(server_time)s] %(message)s',
            },
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'django.server': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'django.server',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'propagate': True,
            },
            'django.server': {
                'handlers': ['django.server'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['mail_admins', 'console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'INFO'
            },
        }
    }

    # Custom user app
    AUTH_USER_MODEL = 'users.User'

    # Django Rest Framework
    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
        'PAGE_SIZE': int(os.getenv('DJANGO_PAGINATION_LIMIT', '10')),
        'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ),
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        )
    }

    CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

    CONSTANCE_CONFIG = {
        'PUBLIC_URL': ('', 'Public URL', str),
        'FIRST_RUN': (True, 'First Run', bool),
        'CHANNEL': ('', 'Channel name', str),
        'CHANNEL_ID': ('', 'Channel ID', str),
        'USE_IRC': (False, 'Use IRC for Channel Point Redemption Emotes', bool),
        'SCOPE_UPDATED_NEEDED': (False, 'Need to update Twitch Scopes', bool),
        'SCOPES_REFRESHED': (False, 'Have the tokens just been refreshed?', bool),
        'FORCE_WEBHOOK_REFRESH': (False, 'Force active webhooks to be refreshed', bool),
        'RESET_ALL_WEBHOOKS': (False, 'Force all webhooks to be refreshed (used for migrations)', bool),
        'TWITCH_ACCESS_TOKEN': ('', 'Twitch API Access Token', str),
        'TWITCH_REFRESH_TOKEN': ('', 'Twitch API Refresh Token', str),
        'TWITCH_ACCESS_TOKEN_EXPIRATION': ('', 'Expiration time for Twitch API Access Token', datetime),
        'TWITCH_APP_ACCESS_TOKEN': ('', 'Twitch API App Access Token', str),
        'TWITCH_APP_ACCESS_TOKEN_EXPIRATION': ('', 'Expiration time for Twitch API App Access Token', datetime),
        'TWITCH_APP_REFRESH_TOKEN': ('', 'Twitch API App Refresh Token', str),
        'STATUS_WEBSOCKET': ('INACTIVE', 'Twitch WS Connection Status', str),
        'STATUS_CHANNEL_UPDATE': ('INACTIVE', 'Channel Update Connection Status', str),
        'STATUS_CHANNEL_FOLLOW': ('INACTIVE', 'Channel Follow Connection Status', str),
        'STATUS_CHANNEL_CHEER': ('INACTIVE', 'Channel Cheer Connection Status', str),
        'STATUS_CHANNEL_POINT_REDEMPTION': (
            'INACTIVE', 'Channel Point Redemption Connection Status', str
        ),
        'STATUS_CHANNEL_RAID': ('INACTIVE', 'Channel Raid Connection Status', str),
        'STATUS_CHANNEL_HYPE_TRAIN_BEGIN': ('INACTIVE', 'Hype Train Begin Connection Status', str),
        'STATUS_CHANNEL_HYPE_TRAIN_PROGRESS': (
            'INACTIVE', 'Hype Train Progress Connection Status', str
        ),
        'STATUS_CHANNEL_HYPE_TRAIN_END': ('INACTIVE', 'Hype Train End Connection Status', str),
    }

    TOKEN_SCOPES = [
        'bits:read',
        'channel:read:redemptions',
        'channel:read:hype_train',
        'channel_subscriptions',
        'chat:read',
        'chat:edit'
    ]
