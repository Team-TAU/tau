import os

from constance import config

def base_data(type_value, callback_url, version="1"):
    data = {
        "type": type_value,
        "version": version,
        "condition": {
            "broadcaster_user_id": config.CHANNEL_ID
        },
        "transport": {
            "method": "webhook",
            "callback": callback_url,
            "secret": os.environ.get('TWITCH_WEBHOOK_SECRET', None)
        }
    }
    return data

def stream_online(base_url, streamer_id):
    type_value = 'stream.online'
    url = '{}/api/v1/twitch-events/stream-online/webhook/'.format(base_url)
    data = base_data(type_value, url)
    data['condition']['broadcaster_user_id'] = streamer_id
    return data

def stream_offline(base_url, streamer_id):
    type_value = 'stream.offline'
    url = '{}/api/v1/twitch-events/stream-offline/webhook/'.format(base_url)
    data = base_data(type_value, url)
    data['condition']['broadcaster_user_id'] = streamer_id
    return data

def channel_update(base_url):
    type_value = 'channel.update'
    url = '{}/api/v1/twitch-events/update/webhook/'.format(base_url)
    return base_data(type_value, url)

def channel_follow(base_url):
    type_value = 'channel.follow'
    url = '{}/api/v1/twitch-events/follow/webhook/'.format(base_url)
    return base_data(type_value, url)

def channel_points_redemption(base_url):
    type_value = 'channel.channel_points_custom_reward_redemption.add'
    url = '{}/api/v1/twitch-events/point-redemption/webhook/'.format(base_url)
    return base_data(type_value, url)

def channel_cheer(base_url):
    type_value = 'channel.cheer'
    url = '{}/api/v1/twitch-events/cheer/webhook/'.format(base_url)
    return base_data(type_value, url)

def channel_raid(base_url):
    type_value = 'channel.raid'
    version = 'beta'
    url = '{}/api/v1/twitch-events/raid/webhook/'.format(base_url)
    data = base_data(type_value, url, version)

    # Change 'broadcaster_user_id' key to 'to_broadcaster_user_id'
    data['condition']['to_broadcaster_user_id'] = data['condition']['broadcaster_user_id']
    del data['condition']['broadcaster_user_id']

    return data

def channel_hype_train_begin(base_url):
    type_value = 'channel.hype_train.begin'
    url = '{}/api/v1/twitch-events/hype-train-begin/webhook/'.format(base_url)
    return base_data(type_value, url)

def channel_hype_train_progress(base_url):
    type_value = 'channel.hype_train.progress'
    url = '{}/api/v1/twitch-events/hype-train-progress/webhook/'.format(base_url)
    return base_data(type_value, url)

def channel_hype_train_end(base_url):
    type_value = 'channel.hype_train.end'
    url = '{}/api/v1/twitch-events/hype-train-end/webhook/'.format(base_url)
    return base_data(type_value, url)
