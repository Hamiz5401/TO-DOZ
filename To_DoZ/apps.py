from django.apps import AppConfig


class ToDozConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'To_DoZ'

    def ready(self):
        from aps_scheduler import scheduler
        scheduler.start()

