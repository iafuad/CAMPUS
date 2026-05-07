from django.contrib import admin
from .models import (
    ExchangeMatch,
    ExchangeMatchStatus,
    ExchangePost,
    ExchangePostStatus,
    ExchangeSession,
    ExchangeSessionStatus,
    MatchDecision,
    MatchDecisionStatus,
    SessionFeedback,
    SessionFeedbackStatus,
    Skill,
)

admin.site.register(Skill)
admin.site.register(ExchangePost)
admin.site.register(ExchangePostStatus)
# admin.site.register(UserSkill)
admin.site.register(ExchangeMatch)
admin.site.register(ExchangeMatchStatus)
admin.site.register(ExchangeSession)
admin.site.register(ExchangeSessionStatus)
admin.site.register(SessionFeedback)
admin.site.register(SessionFeedbackStatus)
admin.site.register(MatchDecision)
admin.site.register(MatchDecisionStatus)
