"""The user/admin setup follows the 'extending the existing User model' section of django 4.0 docs."""

# Django imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Local application imports
from .models import User, TimetableLeadTeacher


class TimetableLeadTeacherInline(admin.StackedInline):
    """Inline admin descriptor for TimetableLeadTeacher model which acts a bit like a singleton."""
    model = TimetableLeadTeacher
    can_delete = False
    verbose_name_plural = 'timetable_lead_teacher'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (TimetableLeadTeacherInline,)


# Re-register UserAdmin
admin.site.register(User, UserAdmin)
