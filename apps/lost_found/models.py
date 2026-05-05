from django.db import models
from django.conf import settings


# Create your models here.
class LostAndFoundStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class LostAndFoundCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class LostAndFoundPost(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    lost_or_found_date = models.DateField()
    location = models.CharField(max_length=100)
    type = models.CharField(max_length=10)  # 'lost' or 'found'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lost_and_found_posts",
    )
    status = models.ForeignKey(LostAndFoundStatus, on_delete=models.CASCADE)
    category = models.ForeignKey(LostAndFoundCategory, on_delete=models.CASCADE)
    photos = models.ManyToManyField(
        "media.Photo", blank=True, related_name="lost_and_found_posts"
    )

    def __str__(self):
        return self.title


class LostAndFoundMatchStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class LostAndFoundMatch(models.Model):
    status = models.ForeignKey(LostAndFoundMatchStatus, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    lost_post = models.ForeignKey(
        LostAndFoundPost, related_name="lost_post", on_delete=models.CASCADE
    )
    found_post = models.ForeignKey(
        LostAndFoundPost, related_name="found_post", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Match {self.match_id} between Lost Post {self.lost_post.title} and Found Post {self.found_post.title}"


class ClaimRequestStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ClaimRequest(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="claim_requests",
    )
    status = models.ForeignKey(ClaimRequestStatus, on_delete=models.CASCADE)
    found_post = models.ForeignKey(LostAndFoundPost, on_delete=models.CASCADE)
    lost_and_found_match = models.OneToOneField(
        LostAndFoundMatch, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Claim {self.claim_id} for post {self.found_post.id}"


class ClaimThread(models.Model):
    thread = models.OneToOneField("threads.Thread", on_delete=models.CASCADE)
    claim_request = models.OneToOneField(
        ClaimRequest, on_delete=models.CASCADE, related_name="claim_thread"
    )

    def __str__(self):
        return f"Claim Thread for {self.claim_request}"
