"""The user/admin setup follows the 'extending the existing User model' section of django 4.0 docs."""

# Django imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Local application imports
from data import models


class ProfileInline(admin.StackedInline):
    """Inline admin descriptor for TimetableLeadTeacher model which acts a bit like a singleton."""
    model = models.Profile
    can_delete = False
    verbose_name_plural = 'user_profile'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


# Register all models to the admin site
admin.site.register(models.Profile)
admin.site.register(models.School)
admin.site.register(models.Pupil)
admin.site.register(models.Teacher)
admin.site.register(models.Classroom)
admin.site.register(models.TimetableSlot)
admin.site.register(models.FixedClass)
admin.site.register(models.UnsolvedClass)
