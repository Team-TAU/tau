import json
from django.db import migrations

def fix_pubsub_json(apps, schema_editor):
    TwitchEvent = apps.get_model('twitchevents', 'TwitchEvent')
    for event in TwitchEvent.objects.filter(event_source='PubSub'):
        event_data = event.event_data
        if isinstance(event_data['message'], str):
            event_data['message'] = json.loads(event_data['message'])
            event.event_data = event_data
            event.save()

class Migration(migrations.Migration):

    dependencies = [
        ('twitchevents', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_pubsub_json)
    ]
