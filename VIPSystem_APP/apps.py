from django.apps import AppConfig
from django.db.models.signals import post_migrate

class VipsystemAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "VIPSystem_APP"
    
    # def ready(self):
    #     post_migrate.connect(initialize_social_app, sender=self)