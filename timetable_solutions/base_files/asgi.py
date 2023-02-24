"""
ASGI config for timetable project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

# Standard library imports
import os

# Django imports
from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base_files.settings.development")

application = get_asgi_application()
