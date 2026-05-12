from django.urls import path
from . import views

app_name = "forum"

urlpatterns = [
    path("", views.forum_index, name="index"),
    path("create/", views.thread_create, name="thread_create"),
    path("<int:pk>/", views.thread_detail, name="thread_detail"),
    path("messages/<int:message_id>/vote/", views.vote_message, name="vote_message"),
    path("search-suggestions/", views.search_suggestions, name="search_suggestions"),
]
