from django.contrib import admin
from .models import (lost_and_found_status, lost_and_found_category, lost_and_found_post, claim_request_status, claim_request, lost_and_found_match, claim_request_thread)

# Register your models here.
admin.site.register(lost_and_found_status)
admin.site.register(lost_and_found_category)
admin.site.register(lost_and_found_post)
admin.site.register(claim_request_status)
admin.site.register(claim_request)
admin.site.register(lost_and_found_match)
admin.site.register(claim_request_thread)