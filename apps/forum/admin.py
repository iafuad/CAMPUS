from django.contrib import admin

from .models import ForumThread


@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "course",
        "department",
        "trimester",
        "is_announcement",
        "is_pinned",
    )
    search_fields = ("author__email", "course__name", "department__name")
    list_filter = ("is_announcement", "is_pinned", "course", "department", "trimester")
