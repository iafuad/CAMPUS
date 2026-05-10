from django.contrib import admin
from .models import (
    LostAndFoundCategory,
    LostAndFoundPost,
    LostAndFoundPhoto,
    LostAndFoundTag,
    ClaimRequest,
    SuggestedMatch,
    ClaimThread,
)

admin.site.register(LostAndFoundCategory)
admin.site.register(LostAndFoundPost)
admin.site.register(LostAndFoundPhoto)
admin.site.register(LostAndFoundTag)
admin.site.register(ClaimRequest)
admin.site.register(SuggestedMatch)
admin.site.register(ClaimThread)
