from django.db import models
from django.conf import settings
from apps.academics.models import Course, Department, Trimester


# Create your models here.
class ForumThread(models.Model):
    is_announcement = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_threads",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="forum_threads"
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="forum_threads"
    )
    trimester = models.ForeignKey(
        Trimester,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forum_threads",
    )
    thread = models.OneToOneField("threads.Thread", on_delete=models.CASCADE)

    def __str__(self):
        return f"ForumThread(id={self.id}, title={self.thread.title}, author={self.author.email})"
