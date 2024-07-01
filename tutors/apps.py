from django.apps import AppConfig


class TutorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tutors'

    def ready(self):
        import tutors.signals
