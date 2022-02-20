import hmac
import hashlib
import os

def generate_signature(headers, body):
    secret = os.environ.get('TWITCH_WEBHOOK_SECRET', None)
    hmac_message = headers['Twitch-Eventsub-Message-Id'] \
                   + headers['Twitch-Eventsub-Message-Timestamp'] \
                   + body
    signature = hmac.new(
        bytes(secret, 'latin-1'),
        msg=bytes(hmac_message, 'latin-1'),
        digestmod = hashlib.sha256
    ).hexdigest().lower()

    return f'sha256={signature}'

def valid_webhook_request(headers, body):
    signature = generate_signature(headers, body)
    return signature == headers['Twitch-Eventsub-Message-Signature'].lower()
