from django.contrib import admin
from .models import (
    Course,
    Department,
    Section,
    Trimester,
    # UserAdmission,
    # UserCourseEnrollment,
    # UserCourseEnrollmentStatus,
)

admin.site.register(Course)
admin.site.register(Department)
admin.site.register(Section)
admin.site.register(Trimester)
# admin.site.register(UserAdmission)
# admin.site.register(UserCourseEnrollment)
# admin.site.register(UserCourseEnrollmentStatus)
