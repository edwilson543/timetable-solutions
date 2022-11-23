"""
Module declaring the ModelAdmin for each model registered to the custom admin site
"""

# Django imports
from django.contrib import admin

# Local application imports
from .custom_admin_site import user_admin
from .base_model_admin import BaseModelAdmin
from data import models


@admin.register(models.Pupil, site=user_admin)
class PupilAdmin(BaseModelAdmin):
    """
    ModelAdmin for the Pupil model
    """
    list_display = ["firstname", "surname", "year_group", "pupil_id"]
    list_display_links = ["surname"]
