from .models import ExchangePost, ExchangeMatch
from apps.common.choices import ExchangePostStatus


def find_and_create_matches(instance):
    """
    Plain function (not a signal receiver).
    Called manually from post_create and post_edit views,
    AFTER form.save_m2m() so skills are already attached.
    """
    if instance.deleted_at is not None:
        return
    if instance.status != ExchangePostStatus.PENDING:
        return

    new_post = instance

    candidates = ExchangePost.objects.filter(
        deleted_at__isnull=True,
        status=ExchangePostStatus.PENDING,
    ).exclude(
        author=new_post.author
    ).prefetch_related('skills_offered', 'skills_needed')

    new_post_offered = set(new_post.skills_offered.values_list('id', flat=True))
    new_post_needed  = set(new_post.skills_needed.values_list('id', flat=True))

    for candidate in candidates:
        candidate_offered = set(candidate.skills_offered.values_list('id', flat=True))
        candidate_needed  = set(candidate.skills_needed.values_list('id', flat=True))

        new_can_offer       = new_post_offered & candidate_needed
        candidate_can_offer = candidate_offered & new_post_needed

        if new_can_offer and candidate_can_offer:
            ExchangeMatch.objects.get_or_create(
                ex_p_a=new_post,
                ex_p_b=candidate,
            )