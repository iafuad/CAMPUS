from django.contrib import admin
from .models import (
    LostAndFoundStatus,
    LostAndFoundCategory,
    LostAndFoundPost,
    LostAndFoundPhoto,
    ClaimRequestStatus,
    ClaimRequest,
    LostAndFoundMatch,
    LostAndFoundMatchStatus,
    ClaimThread,
)

admin.site.register(LostAndFoundStatus)
admin.site.register(LostAndFoundCategory)
admin.site.register(LostAndFoundPost)
admin.site.register(LostAndFoundPhoto)
admin.site.register(ClaimRequestStatus)
admin.site.register(ClaimRequest)
admin.site.register(LostAndFoundMatch)
admin.site.register(LostAndFoundMatchStatus)
admin.site.register(ClaimThread)
