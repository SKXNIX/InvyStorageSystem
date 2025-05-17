from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'  # Полный Python-путь
    label = 'products'  # Ярлык для использования в INSTALLED_APPS
