#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from django.core.management.commands.runserver import Command as runserver
from django.conf import settings

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tau.config")
    os.environ.setdefault("DJANGO_CONFIGURATION", "Local")
    port = os.environ.get("TAU_PORT", 8000)
    runserver.default_port = port
    runserver.default_addr = "0.0.0.0"

    port = os.environ.get("PORT", 8000)
    addr = os.environ.get("INT_SERVER_ADDR", "0.0.0.0")
    runserver.default_port = port
    runserver.default_addr = addr
    
    try:
        from configurations.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django  # noqa
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
