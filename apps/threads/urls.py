from django.urls import path
from . import views

app_name = "threads"

urlpatterns = [
    path("<int:thread_id>/", views.thread_detail, name="thread_detail"),
]
