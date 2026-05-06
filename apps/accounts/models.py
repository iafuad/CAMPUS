from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["handle"]

    objects = UserManager()


# class AccountStatus(models.Model):
#     name = models.CharField(max_length=50)

#     def save(self, *args, **kwargs):
#         self.name = self.name.capitalize()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.name


class Profile(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("NORMAL", "Normal"),
        ("FLAGGED", "Flagged"),
        ("SUSPENDED", "Suspended"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    first_name = models.CharField(max_length=32, null=True, blank=True)
    last_name = models.CharField(max_length=32, null=True, blank=True)
    student_id = models.IntegerField(unique=True, null=True, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.OneToOneField(
        "media.Photo",
        on_delete=models.CASCADE,
        related_name="profile_picture",
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    is_verified = models.BooleanField(default=False)
    is_graduated = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.email})"
