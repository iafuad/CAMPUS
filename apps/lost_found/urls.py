from django.urls import path
from . import views

app_name = "lost_found"

urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("new/", views.post_create, name="post_create"),
    path("<int:post_id>/", views.post_detail, name="post_detail"),
    path("<int:post_id>/claim/", views.submit_claim, name="submit_claim"),
]
