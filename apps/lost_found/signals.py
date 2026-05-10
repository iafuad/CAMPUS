"""
Lost & Found — Signal registration
====================================
Register this module in your app config:

    # apps/lost_found/apps.py
    class LostFoundConfig(AppConfig):
        name = "apps.lost_found"

        def ready(self):
            import apps.lost_found.signals  # noqa: F401

The signal below is intentionally lightweight: it only handles the edge case
where a post transitions to APPROVED status outside of the normal create-view
flow (e.g., admin approval, a moderation action).

For posts created through post_create or post_edit views, run_auto_match()
is called directly in the view *after* form.save_m2m() so that tag data is
already available — signals fire before M2M is committed.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import LostAndFoundPost
from .matching import run_auto_match
from apps.common.choices import LostAndFoundStatus


@receiver(post_save, sender=LostAndFoundPost)
def auto_match_on_approval(sender, instance, created, update_fields, **kwargs):
    """
    Trigger auto-matching when a post reaches APPROVED status.

    Skipped when update_fields is specified and 'status' is not in it,
    to avoid running unnecessarily on every field-level save (e.g., soft deletes).

    Note: tags are a M2M relation and may not be populated yet if this signal
    fires during the initial create-view flow.  The view handles that case
    directly; this signal covers admin/moderation approvals.
    """
    if update_fields and "status" not in update_fields:
        return

    if instance.status == LostAndFoundStatus.APPROVED and not instance.deleted_at:
        suggestions = run_auto_match(instance)

        # TODO — Notification hook for admin-approved posts:
        # for suggestion in suggestions:
        #     notify_user(recipient=suggestion.lost_post.user, verb="suggested_match", target=suggestion)
