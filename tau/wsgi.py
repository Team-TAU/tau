"""
WSGI config for tau project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/gunicorn/
"""
import os
from configurations.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tau.config")
os.environ.setdefault("DJANGO_CONFIGURATION", "Production")

application = get_wsgi_application()
