from django.conf import settings
from django.db import models
from apps.common.choices import (
    ExchangePostStatus,
    ExchangeMatchStatus,
    ExchangeSessionStatus,
    SessionFeedbackStatus,
    MatchDecisionStatus,
)


class Skill(models.Model):
    skill_name = models.CharField(max_length=100)
    description = models.TextField()


class ExchangePost(models.Model):
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    users_post = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exchange_posts",
    )
    skills_offered = models.ManyToManyField(
        Skill,
        related_name="offered_in_posts",
    )
    skills_requested = models.ManyToManyField(
        Skill,
        related_name="requested_in_posts",
    )
    status = models.CharField(
        max_length=20,
        choices=ExchangePostStatus.choices,
        default=ExchangePostStatus.PENDING,
    )


# class UserSkill(models.Model):
#    proficiency_level = models.PositiveSmallIntegerField()
#    proficiency_method = models.CharField(max_length=50)
#    proficiency_notes = models.TextField(null=True, blank=True)
#    years_experience = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

#    user = models.ForeignKey(
#        settings.AUTH_USER_MODEL,
#        on_delete=models.CASCADE,
#        related_name="user_skills",
#    )
#    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)


class ExchangeMatch(models.Model):
    matched_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=ExchangeMatchStatus.choices,
        default=ExchangeMatchStatus.PENDING,
    )
    ex_p_a = models.ForeignKey(
        ExchangePost, related_name="exchange_post_a", on_delete=models.CASCADE
    )
    ex_p_b = models.ForeignKey(
        ExchangePost, related_name="exchange_post_b", on_delete=models.CASCADE
    )


class ExchangeSession(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    match = models.OneToOneField(ExchangeMatch, on_delete=models.CASCADE)
    thread = models.OneToOneField("threads.Thread", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=ExchangeSessionStatus.choices,
        default=ExchangeSessionStatus.PENDING,
    )


class SessionFeedback(models.Model):
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    comment = models.TextField(null=True, blank=True)
    given_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    rater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback_given",
    )
    rated_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback_received",
    )
    exchange_session = models.ForeignKey(ExchangeSession, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=SessionFeedbackStatus.choices,
        default=SessionFeedbackStatus.PENDING,
    )


class MatchDecision(models.Model):
    decided_at = models.DateTimeField(auto_now_add=True)

    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="match_decisions",
    )
    status = models.CharField(
        max_length=20,
        choices=MatchDecisionStatus.choices,
        default=MatchDecisionStatus.PENDING,
    )
    exchange_match = models.ForeignKey(ExchangeMatch, on_delete=models.CASCADE)
