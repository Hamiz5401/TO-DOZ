from django.apps import AppConfig


class ToDozConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'To_DoZ'

    def ready(self):
        from .scheduler import scheduler
        scheduler.start()
        from .jobs import add_job
        from .jobs import add_noti_discord

