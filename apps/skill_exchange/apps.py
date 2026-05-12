from django.apps import AppConfig

class SkillExchangeConfig(AppConfig):
    name = "apps.skill_exchange"
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "Skill Exchange"

    def ready(self):
        # Signals are not used currently, matching is done manually in views
        pass