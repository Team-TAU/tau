import json
from django.core.management.base import BaseCommand

from tau.twitch.models import TwitchAPIScope, TwitchHelixEndpoint

class Command(BaseCommand):
    help = 'Import the helix_endpoints.json file to the database, updating existing, and creating new endpoints and scopes.'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs=1, type=str)

    def handle(self, *args, **kwargs):
        filename = kwargs['filename'][0]
        print(f'===== Opening {filename} to check for new Twitch Helix API Scopes. =====')
        with open(filename,) as f:
            data = json.load(f)

        scope_set = set([row['scope'] for row in data])
        existing_scopes = set(TwitchAPIScope.objects.all().values_list('scope', flat=True))
        new_scopes = list(scope_set - existing_scopes)
        for scope in new_scopes:
            if scope is not None:
                TwitchAPIScope.objects.create(scope=scope)
        print(f'  {len(new_scopes)-1} new scopes found and created.')
        scopes_by_scope = { row.scope: row for row in TwitchAPIScope.objects.all() }

        TwitchHelixEndpoint.objects.all().delete()
        for endpoint in data:
            if endpoint['token_type'] == 'OAuth':
                token_type = 'OA'
            elif endpoint['token_type'] == 'AppAccess':
                token_type = 'AP'

            if endpoint['scope'] is not None:
                scope = scopes_by_scope[endpoint['scope']]
            else:
                scope = None

            TwitchHelixEndpoint.objects.create(
                description=endpoint['description'],
                endpoint=endpoint['endpoint'],
                method=endpoint['method'],
                reference_url=endpoint['reference_url'],
                token_type=token_type,
                scope=scope
            )
