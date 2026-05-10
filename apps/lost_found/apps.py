from django.apps import AppConfig


class LostFoundConfig(AppConfig):
    auto_field = "django.db.models.BigAutoField"
    name = "apps.lost_found"

    def ready(self):
        import apps.lost_found.signals  # noqa
