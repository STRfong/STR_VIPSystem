from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os

class Command(BaseCommand):
    help = 'Adds a Google social app using environment variables'

    def handle(self, *args, **options):
        # Get credentials from environment variables
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        secret = os.environ.get('GOOGLE_SECRET_KEY')

        if not client_id or not secret:
            self.stdout.write(self.style.ERROR('GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set in environment variables'))
            return

        # Create or update the SocialApp
        social_app, created = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': secret,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Created new Google social app'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated existing Google social app'))

        # Get the current site
        current_site = Site.objects.get_current()

        # Add the social app to the site
        social_app.sites.add(current_site)

        self.stdout.write(self.style.SUCCESS(f'Added Google social app to site: {current_site.name}'))