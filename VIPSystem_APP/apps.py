from django.apps import AppConfig
from django.db.models.signals import post_migrate

def initialize_social_app(sender, **kwargs):
    from .models import CustomSocialApp
    CustomSocialApp.get_or_create_app('google')

class VipsystemAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "VIPSystem_APP"

    def ready(self):
        post_migrate.connect(initialize_social_app, sender=self)