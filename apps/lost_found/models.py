from django.db import models
from django.conf import settings
from apps.common.choices import (
    LostAndFoundStatus,
    LostAndFoundMatchStatus,
    ClaimRequestStatus,
    LostAndFoundPostType,
)


class LostAndFoundCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class LostAndFoundTag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class LostAndFoundPost(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    lost_or_found_date = models.DateField()
    location = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=LostAndFoundPostType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lost_and_found_posts",
    )
    status = models.CharField(
        max_length=20,
        choices=LostAndFoundStatus.choices,
        default=LostAndFoundStatus.PENDING,
    )
    category = models.ForeignKey(LostAndFoundCategory, on_delete=models.CASCADE)
    tags = models.ManyToManyField(LostAndFoundTag, blank=True)

    def __str__(self):
        return self.title


class LostAndFoundPhoto(models.Model):
    post = models.ForeignKey(
        LostAndFoundPost,
        on_delete=models.CASCADE,
        related_name="post_photos",
    )

    photo = models.ForeignKey(  # allow reuse
        "media.Photo",
        on_delete=models.CASCADE,
        related_name="lost_found_attachments",
    )

    order = models.PositiveIntegerField(default=0)


class LostAndFoundMatch(models.Model):
    status = models.CharField(
        max_length=20,
        choices=LostAndFoundMatchStatus.choices,
        default=LostAndFoundMatchStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    lost_post = models.ForeignKey(
        LostAndFoundPost, related_name="lost_post", on_delete=models.CASCADE
    )
    found_post = models.ForeignKey(
        LostAndFoundPost, related_name="found_post", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Match {self.id} between Lost Post {self.lost_post.id} and Found Post {self.found_post.id}"  # type: ignore


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
    status = models.CharField(
        max_length=20,
        choices=ClaimRequestStatus.choices,
        default=ClaimRequestStatus.PENDING,
    )
    found_post = models.ForeignKey(LostAndFoundPost, on_delete=models.CASCADE)
    lost_and_found_match = models.OneToOneField(
        LostAndFoundMatch, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Claim {self.id} for post {self.found_post.id} through match {self.lost_and_found_match.id}"  # type: ignore


class ClaimThread(models.Model):
    thread = models.OneToOneField("threads.Thread", on_delete=models.CASCADE)
    claim_request = models.OneToOneField(
        ClaimRequest, on_delete=models.CASCADE, related_name="claim_thread"
    )

    def __str__(self):
        return f"Claim Thread for claim request {self.claim_request.id}"  # type: ignore
