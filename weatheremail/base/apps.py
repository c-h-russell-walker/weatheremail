from django.apps import AppConfig


class BaseAppConfig(AppConfig):
    name = 'base'

    def ready(self):
        import base.signals