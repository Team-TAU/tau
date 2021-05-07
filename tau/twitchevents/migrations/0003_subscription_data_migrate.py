import json
from django.db import migrations
from copy import deepcopy

def fix_pubsub_json_again(apps, schema_editor):
    TwitchEvent = apps.get_model('twitchevents', 'TwitchEvent')
    for event in TwitchEvent.objects.filter(event_source='PubSub'):
        event_data = event.event_data
        if "message" in event_data:
            data = deepcopy(event_data)
            event_data = {
                "type": "MESSAGE",
                "data": data
            }
            event.event_data = event_data
            event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('twitchevents', '0002_auto_20210429_1457'),
    ]

    operations = [
        migrations.RunPython(fix_pubsub_json_again)
    ]
