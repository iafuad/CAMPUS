from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from apps.common.choices import ProfileStatus


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        if not extra_fields.get("first_name"):
            raise ValueError("First name is required")

        if not extra_fields.get("last_name"):
            raise ValueError("Last name is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    handle = models.CharField(max_length=50, unique=True)

    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["handle", "first_name", "last_name"]

    objects = UserManager()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    student_id = models.IntegerField(unique=True, null=True, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.OneToOneField(
        "media.Photo",
        on_delete=models.CASCADE,
        related_name="profile_picture",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=ProfileStatus.choices,
        default=ProfileStatus.PENDING,
    )
    rank = models.ForeignKey(
        "rankings.UserRank", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_verified = models.BooleanField(default=False)
    is_graduated = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.email})"
