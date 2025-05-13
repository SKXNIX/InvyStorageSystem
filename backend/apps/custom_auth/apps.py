from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.custom_auth'
    label = 'custom_auth' # Уникальный label для избежания конфликтов
                          #со встроенным модулем auth Django
