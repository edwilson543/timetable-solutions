"""
Import all model admins and the admin site, so that django can discover them
"""
# Custom admin site
from .custom_admin_site import CustomAdminSite, user_admin

# Model admins
from .other_model_admins import (
    PupilAdmin,
    TeacherAdmin,
    ClassroomAdmin,
    TimetableSlotAdmin,
)
from .lesson_model_admin import LessonAdmin
from .profile_model_admin import ProfileAdmin
