from django.apps import AppConfig
from django.dispatch import receiver

class VipsystemAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "VIPSystem_APP"
    
    def ready(self):
        # 導入信號模塊
        import VIPSystem_APP.adapter
