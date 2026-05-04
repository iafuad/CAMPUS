from django.contrib import admin
from .models import (
    Thread,
    ThreadMessage,
    MessageVote,
    MessageAttachment,
    ThreadParticipant,
    Tag,
)


class ThreadMessageInline(admin.TabularInline):
    model = ThreadMessage
    extra = 0
    readonly_fields = ("sender", "content", "sent_at")


class MessageAttachmentInline(admin.TabularInline):
    model = MessageAttachment
    extra = 0


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_by", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "description")

    inlines = [ThreadMessageInline]

    readonly_fields = ("created_at", "updated_at")


@admin.register(ThreadMessage)
class ThreadMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "thread", "sender", "short_content", "sent_at")
    list_filter = ("sent_at",)
    search_fields = ("content",)

    inlines = [MessageAttachmentInline]

    readonly_fields = ("sent_at", "updated_at")

    def short_content(self, obj):
        return obj.content[:50]


@admin.register(MessageVote)
class MessageVoteAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "user", "vote_type", "created_at")
    list_filter = ("vote_type",)


@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "photo")


@admin.register(ThreadParticipant)
class ThreadParticipantAdmin(admin.ModelAdmin):
    list_display = ("thread", "user", "role", "joined_at")
    list_filter = ("role",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)
