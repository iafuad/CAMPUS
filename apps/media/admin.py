from django.contrib import admin
from django.utils.html import format_html
from .models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "thumbnail", "uploaded_by", "uploaded_at", "is_deleted")
    list_filter = ("is_deleted", "uploaded_at")
    search_fields = ("uploaded_by__email", "uploaded_by__handle")
    readonly_fields = ("uploaded_at",)
