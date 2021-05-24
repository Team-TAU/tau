#!/usr/bin/env python
"""Tau's command line utility to validate environment variables"""
import os
import sys
import logging

# TWITCH SECRET LENGTH 10->100
# if DJANGO_DB_TYPE=POSTGRES, NEED DJANGO_DB, DJANGO_DB_USER, DJANGO_DB_PW, DJANGO_DB_URL
# if DJANGO_DB_TYPE=sqlite, nothing else required
# if USE_NGROK=TRUE, MUST HAVE USE_NGROK_TOKEN. IF USE_NGROK_TOKEN=TRUE, NEED NGROK_TOKEN
# PROPOSED: USE_NGROK=TRUE BY DEFAULT. IF NGROK_TOKEN IS SET, USE IT.

def main():
    errors = []
    warnings = []
    DB_TYPE = os.environ.get("DJANGO_DB_TYPE","postgres")
    if DB_TYPE == "postgres":
        if "" == os.environ.get("DJANGO_DB",""):
            errors.append("Missing environment setting DJANGO_DB (Django Database Name)")
        if "" == os.environ.get("DJANGO_DB_USER",""):
            errors.append("Missing environment setting DJANGO_DB_USER (Django Database Username)")
        if "" == os.environ.get("DJANGO_DB_PW",""):
            errors.append("Missing environment setting DJANGO_DB_PW (Django Database Password)")
        if "" == os.environ.get("DJANGO_DB_URL",""):
            errors.append("Missing environment setting DJANGO_DB_URL (Django Database URL)")
    if DB_TYPE != "postgres" and DB_TYPE != "sqlite3":
        errors.append("Invalid environment setting DJANGO_DB_TYPE (Django Database Type). "
        +"Must be equal to \"postgres\" or \"sqlite3\" and is currently set to \""+DB_TYPE+"\"")

    if "" == os.environ.get("TWITCH_APP_ID",""):
        errors.append("Missing environment setting TWITCH_APP_ID (Twitch App ID)")
    if "" == os.environ.get("TWITCH_CLIENT_SECRET",""):
        errors.append("Missing environment setting TWITCH_CLIENT_SECRET (Twitch Client Secret)")
    TWITCH_WEBHOOK_SECRET = os.environ.get("TWITCH_WEBHOOK_SECRET","")
    if "" == TWITCH_WEBHOOK_SECRET:
        errors.append("Missing environment setting TWITCH_WEBHOOK SECRET (Twitch Webhook Secret)")
    if len(TWITCH_WEBHOOK_SECRET) < 10 or len(TWITCH_WEBHOOK_SECRET) > 100:
        errors.append("Environment setting TWITCH_WEBHOOK_SECRET must be between 10 and 100 characters")

    if "True" == os.environ.get("USE_NGROK","True") and "" == os.environ.get("NGROK_TOKEN",""):
        warnings.append("For best results, consider entering an NGROK_TOKEN. This is available with a free sign-up on https://ngrok.io")

    if "" != os.environ.get("REDIS_ENDPOINT") and "" == os.environ.get("REDIS_PW"):
        errors.append("When environment setting REDIS_ENDPOINT is in use, the setting REDIS_PW must also be set.")
    if "" != os.environ.get("REDIS_SERVER") and "" != os.environ.get("REDIS_ENDPOINT"):
        warnings.append("When environment setting REDIS_ENDPOINT is in use, it will supercede environment setting REDIS_SERVER.")
    if len(warnings) > 0:
        [logging.warning(warning) for warning in warnings]
    if len(errors) > 0:
        [logging.error(error) for error in errors]
        sys.exit(1)
    sys.exit(0)
if __name__ == '__main__':
    main()