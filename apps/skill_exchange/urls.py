from django.urls import path

from . import views

app_name = "skill_exchange"

urlpatterns = [
    path("posts/", views.post_list, name="post_list"),
    path("posts/new/", views.post_create, name="post_create"),
    path("posts/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path("matches/", views.match_list, name="match_list"),
    path("matches/<int:match_id>/", views.match_detail, name="match_detail"),
    path("matches/<int:match_id>/decision/", views.match_decision, name="match_decision"),
    path("sessions/<int:session_id>/", views.session_detail, name="session_detail"),
    path("sessions/<int:session_id>/end-request/", views.session_end_request, name="session_end_request"),
    path("sessions/<int:session_id>/end-decision/", views.session_end_decision, name="session_end_decision"),
    path("sessions/<int:session_id>/feedback/", views.session_feedback_form, name="session_feedback_form"),
    path("feedback/", views.user_feedback_summary, name="user_feedback_summary"),
]
