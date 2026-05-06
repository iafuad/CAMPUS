from django.conf import settings
from django.db import models


class ThreadStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Thread(models.Model):
    VISIBILITY_CHOICES = [
        ("PUBLIC", "Public"),
        ("PRIVATE", "Private"),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="PUBLIC",
    )

    status = models.ForeignKey(
        ThreadStatus, on_delete=models.PROTECT, related_name="threads"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_threads",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    tags = models.ManyToManyField("Tag", blank=True, related_name="threads")

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class ThreadMessageStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ThreadMessage(models.Model):
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="messages"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )

    content = models.TextField()

    reply_to = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    status = models.ForeignKey(
        ThreadMessageStatus, on_delete=models.PROTECT, related_name="messages"
    )

    upvote_count = models.PositiveIntegerField(default=0)
    downvote_count = models.PositiveIntegerField(default=0)

    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Message {self.id} in Thread {self.thread.id} by {self.sender.username}"


class VoteStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MessageVote(models.Model):
    VOTE_TYPE_CHOICES = [
        ("UPVOTE", "Upvote"),
        ("DOWNVOTE", "Downvote"),
    ]

    message = models.ForeignKey(
        ThreadMessage, on_delete=models.CASCADE, related_name="votes"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="message_votes"
    )

    vote_type = models.CharField(max_length=10, choices=VOTE_TYPE_CHOICES)

    status = models.ForeignKey(
        VoteStatus, on_delete=models.PROTECT, related_name="votes"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("message", "user")  # one vote per user

    def __str__(self):
        return f"{self.user} → {self.vote_type}"


class ThreadParticipant(models.Model):
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="participants"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="thread_participations",
    )

    role = models.CharField(max_length=50, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("thread", "user")


class MessageAttachment(models.Model):
    message = models.ForeignKey(
        ThreadMessage, on_delete=models.CASCADE, related_name="attachments"
    )

    photo = models.ForeignKey(
        "media.Photo", on_delete=models.CASCADE, related_name="message_attachments"
    )

    order = models.PositiveIntegerField(default=0)
