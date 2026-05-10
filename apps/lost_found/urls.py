from django.urls import path
from . import views

app_name = "lost_found"

urlpatterns = [
    # ── Post browsing ──────────────────────────────────────────────────────
    path("", views.post_list, name="post_list"),
    path("new/", views.post_create, name="post_create"),
    path("<int:post_id>/", views.post_detail, name="post_detail"),
    # ── Manual claim flow ──────────────────────────────────────────────────
    # POST: submit a claim against a found post
    path("<int:post_id>/claim/", views.submit_claim, name="submit_claim"),
    # Found-post owner: view all claims on their post
    path("<int:post_id>/claims/", views.review_claims, name="review_claims"),
    # Found-post owner: approve one specific claim (GET = confirm, POST = execute)
    path(
        "<int:post_id>/claims/<int:claim_id>/approve/",
        views.approve_claim,
        name="approve_claim",
    ),
    # ── Auto-match suggestions (lost-post owner) ───────────────────────────
    # Dashboard of pending suggestions across all the user's lost posts
    path("my-matches/", views.my_suggested_matches, name="my_suggested_matches"),
    # Dismiss a single suggestion
    path(
        "my-matches/<int:suggestion_id>/dismiss/",
        views.dismiss_suggested_match,
        name="dismiss_suggested_match",
    ),
    path("my-posts/", views.my_posts, name="my_posts"),
    path("my-claims/", views.my_claims, name="my_claims"),
]
