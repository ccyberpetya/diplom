# apps.py - ДОЛЖНО БЫТЬ ТАК
from django.apps import AppConfig


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

    # Уберите метод ready() или оставьте пустым
    def ready(self):
        pass