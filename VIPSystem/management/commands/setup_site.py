from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Set up the Site model'

    def handle(self, *args, **options):
        Site.objects.update_or_create(
            id=2,
            defaults={
                'domain': 'https://str-vipststem.zeabur.app',
                'name': 'Zeabur',
            }
        )
        self.stdout.write(self.style.SUCCESS('Successfully set up the google Site model'))
        Site.objects.update_or_create(
            id=1,
            defaults={
                'domain': 'http://127.0.0.1:8000',
                'name': 'localhost',
            }
        )
        self.stdout.write(self.style.SUCCESS('Successfully set up the localhost Site model'))
