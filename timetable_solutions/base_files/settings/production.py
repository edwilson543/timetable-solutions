"""
Settings specific to the production environment.
python-decouple's config is used extensively to retrieve environment variables.
"""

# Third party imports
from decouple import config

# Django imports
from django.contrib import messages

from .base_settings import *


# Basic django settings
ALLOWED_HOSTS = [
    "0.0.0.0",
    "localhost",  # For running production environment locally with docker
    ".timetable-solutions.com",
]
# Tell django the htp header indicating whether the request came from https
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DEBUG = int(config("DEBUG"))

MESSAGE_LEVEL = messages.INFO

SECRET_KEY = config("SECRET_KEY")
# Databases settings -> postgresql in production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_NAME"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST"),
        "PORT": int(config("POSTGRES_PORT")),
    }
}
