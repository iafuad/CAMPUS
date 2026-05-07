from django.urls import path
from . import views

from . import views

urlpatterns = [
    path("", views.forum_index, name="forum index"),
]
