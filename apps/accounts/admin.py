from django.contrib import admin
from .models import Profile, User

admin.site.register(User)
# admin.site.register(AccountStatus)
admin.site.register(Profile)
