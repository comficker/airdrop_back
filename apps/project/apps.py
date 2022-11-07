from django.apps import AppConfig


class ProjectConfig(AppConfig):
    name = 'apps.project'

    def ready(self):
        from apps.project import signals
