#!/usr/bin/env python
"""Tau's command line utility to validate environment variables"""
import os
import sys
import logging

def check_exists(errors,name,label):
    if "" == os.environ.get(name):
        errors.append(f"Missing environment setting {name} ({label})")

def check_length(errors,name,label,min=10,max=100):
    value = os.environ.get(name)
    if(len(value) < min or len(value) > max):
        errors.append(f"Environment setting {name} must be between {min} and {max} characters.")

def main():
    errors = []
    warnings = []
    # Twitch Settings
    check_exists(errors,"TWITCH_APP_ID","Twitch App ID")
    check_exists(errors,"TWITCH_CLIENT_SECRET","Twitch Client Secret")
    check_exists(errors,"TWITCH_WEBHOOK_SECRET","Twitch Webhook Secret")
    
    # Database Settings
    DB_TYPE = os.environ.get("DJANGO_DB_TYPE","postgres")
    if DB_TYPE == "postgres":
        check_exists(errors,"POSTGRES_PW","Postgres Root Password")
        check_exists(errors,"DJANGO_DB_PW","Django Database Password")
        check_exists(errors,"DJANGO_SECRET_KEY","Django Encryption Key")
    if DB_TYPE != "postgres" and DB_TYPE != "sqlite3":
        errors.append("Invalid environment setting DJANGO_DB_TYPE (Django Database Type). "
        +"Must be equal to \"postgres\" or \"sqlite3\" and is currently set to \""+DB_TYPE+"\"")

    # REDIS Settings
    if "" != os.environ.get("REDIS_ENDPOINT") and "" == os.environ.get("REDIS_PW"):
        errors.append("When environment setting REDIS_ENDPOINT is in use, the setting REDIS_PW must also be set.")
    if "" != os.environ.get("REDIS_SERVER") and "" != os.environ.get("REDIS_ENDPOINT"):
        warnings.append("When environment setting REDIS_ENDPOINT is in use, it will supercede environment setting REDIS_SERVER.")

    # Log warnings and errors. Exit with errors if necessary.
    if len(warnings) > 0:
        [logging.warning(warning) for warning in warnings]
    if len(errors) > 0:
        [logging.error(error) for error in errors]
        sys.exit(1)
    sys.exit(0)
if __name__ == '__main__':
    main()