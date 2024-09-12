from django.apps import AppConfig


class VipsystemAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "VIPSystem_APP"

    def ready(self):
        from .models import CustomSocialApp
        CustomSocialApp.get_or_create_app('google')