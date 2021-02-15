import hmac
import hashlib
import os

def valid_webhook_request(headers, body):
    secret = os.environ.get('TWITCH_WEBHOOK_SECRET', None)
    hmac_message = headers['Twitch-Eventsub-Message-Id'] \
                   + headers['Twitch-Eventsub-Message-Timestamp'] \
                   + body
    signature = hmac.new(
        bytes(secret, 'latin-1'),
        msg=bytes(hmac_message, 'latin-1'),
        digestmod = hashlib.sha256
    ).hexdigest().lower()

    matching = 'sha256='+signature == headers['Twitch-Eventsub-Message-Signature'].lower()

    return matching
