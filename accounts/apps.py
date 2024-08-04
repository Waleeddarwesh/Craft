from django.apps import AppConfig


class CourseConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        import accounts.signals
