"""
Import all model admins and the admin site, so that django can discover them
"""
# Custom admin site
from .custom_admin_site import CustomAdminSite, user_admin

# Model admins
from .model_admins import PupilAdmin
