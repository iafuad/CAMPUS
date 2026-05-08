from django.urls import path

from . import views

app_name = "skill_exchange"

urlpatterns = [
    path("", views.index, name="index"),
    path("posts/", views.post_list, name="post_list"),
    path("posts/new/", views.post_create, name="post_create"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("matches/", views.match_list, name="match_list"),
    path("matches/<int:match_id>/", views.match_detail, name="match_detail"),
    path("sessions/<int:session_id>/", views.session_detail, name="session_detail"),
    path(
        "sessions/<int:session_id>/feedback/new/",
        views.feedback_create,
        name="feedback_create",
    ),
]
