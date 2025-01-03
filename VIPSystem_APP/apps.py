from django.apps import AppConfig

class VipsystemAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'VIPSystem_APP'

    def ready(self):
        try:
            from . import signals  # 導入signals
            print("Signals loaded successfully")  # 添加日誌
        except Exception as e:
            print(f"Error loading signals: {str(e)}")  # 添加錯誤日誌