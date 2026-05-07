from django.urls import path
from django.contrib.auth import views as auth_views
from .views import myself, profile_view, register

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),
    path("myself/", myself, name="myself"),
    path("profile/<str:handle>/", profile_view, name="profile"),
]
