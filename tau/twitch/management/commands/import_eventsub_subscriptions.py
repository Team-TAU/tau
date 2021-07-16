import json
from django.core.management.base import BaseCommand

from tau.twitch.models import TwitchAPIScope, TwitchEventSubSubscription

class Command(BaseCommand):
    help = 'Import the Twitch EventSub Subscription data to the database, updating existing, and creating new subscriptions and scopes.'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs=1, type=str)
    
    def handle(self, *args, **kwargs):
        filename = kwargs['filename'][0]
        print(f'===== Opening {filename} to check for new Twitch EventSub Subscriptions and Scopes. =====')
        with open(filename,) as f:
            data = json.load(f)
        
        data_subs = [es['name'] for es in data]
        existing_subs = {es.name: es.id for es in TwitchEventSubSubscription.objects.all()}
        to_delete = list(set(existing_subs.keys()) - set(data_subs))
        counts = {'created': 0, 'updated': 0, 'deleted': 0}
        for sub in data:
            if sub['name'] in existing_subs:
                # Update the existing entry
                TwitchEventSubSubscription.objects.filter(
                    pk=existing_subs[sub['name']]
                ).update(
                    **sub,
                    lookup_name=sub['name'].replace('.', '-')
                )
                counts['updated'] += 1
            else:
                # Create a new entry
                TwitchEventSubSubscription.objects.create(
                    **sub,
                    lookup_name=sub['name'].replace('.', '-')
                )
                counts['created'] += 1

        for name in to_delete:
            TwitchEventSubSubscription.objects.get(name=name).delete()
            counts['deleted'] += 1

        print(f'    {counts["created"]} created, {counts["updated"]} updated, {counts["deleted"]} deleted')    
