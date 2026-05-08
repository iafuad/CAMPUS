from django.contrib import admin
from .models import (
    LostAndFoundCategory,
    LostAndFoundPost,
    LostAndFoundPhoto,
    ClaimRequest,
    LostAndFoundMatch,
    ClaimThread,
)

admin.site.register(LostAndFoundCategory)
admin.site.register(LostAndFoundPost)
admin.site.register(LostAndFoundPhoto)
admin.site.register(ClaimRequest)
admin.site.register(LostAndFoundMatch)
admin.site.register(ClaimThread)
