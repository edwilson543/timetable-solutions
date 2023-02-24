"""
Import all model admins and the admin site, so that django can discover them
"""
# Custom admin site
from .custom_admin_site import CustomAdminSite, user_admin
from .lesson_model_admin import LessonAdmin

# Model admins
from .other_model_admins import (
    ClassroomAdmin,
    PupilAdmin,
    TeacherAdmin,
    TimetableSlotAdmin,
)
from .profile_model_admin import ProfileAdmin
