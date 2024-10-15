from django.apps import AppConfig

class SetdroneConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'setdrone'

    def ready(self):
        import setdrone.signals




