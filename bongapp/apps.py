from django.apps import AppConfig


class BongappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bongapp'
    
    def ready(self):
        import bongapp.signals