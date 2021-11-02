# Generated by Django 3.1.7 on 2021-10-29 01:14

from django.db import migrations

EVENT_MAP = {
    'update': 'channel-update',
    'follow': 'channel-follow',
    'point-redemption': 'channel-channel_points_custom_reward_redemption-add',
    'cheer': 'channel-cheer',
    'raid': 'channel-raid',
    'hype-train-progress': 'channel-hype_train-progress',
    'hype-train-begin': 'channel-hype_train-begin',
    'hype-train-end': 'channel-hype_train-end'
}

def update_event_types(apps, schema_editor):
    TwitchEvent = apps.get_model('twitchevents', 'TwitchEvent')
    for event_type in EVENT_MAP:
        TwitchEvent.objects.filter(
            event_type=event_type
        ).update(
            event_type=EVENT_MAP[event_type]
        )


class Migration(migrations.Migration):
    dependencies = [
        ('twitchevents', '0003_subscription_data_migrate'),
    ]

    operations = [
        migrations.RunPython(update_event_types)
    ]