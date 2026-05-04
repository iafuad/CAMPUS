from django.conf import settings
from django.db import models


def upload_to(instance, filename):
    # Optional: organize uploads by user
    return f"uploads/user_{instance.uploaded_by_id}/{filename}"


class Photo(models.Model):
    file = models.ImageField(upload_to=upload_to)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_photos",
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # soft delete

    def __str__(self):
        return f"Photo {self.id} by {self.uploaded_by}"
