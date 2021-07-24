import os

from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Copies vue generated dashboard html/js/css files to proper django dashboard directories.'

    def handle(self, *args, **kwargs):
        templates_dir = f'{settings.BASE_DIR}/dashboard/templates/dashboard'
        static_dir = f'{settings.BASE_DIR}/dashboard/static'
        source_dir = f'{settings.BASE_DIR}/../tau-dashboard/dist'
        print('Copying compiled dashboard Vue app to templates/static...')
        os.system(f'mkdir -p {templates_dir}')
        os.system(f'cp -v {source_dir}/index.html {templates_dir}')
        if os.path.exists(static_dir):
            os.system(f'rm -rf {static_dir}')
        os.system(f'cp -rf -v {source_dir}/static {static_dir}')

