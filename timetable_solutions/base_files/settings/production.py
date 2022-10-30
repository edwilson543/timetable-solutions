"""
Settings specific to the production environment
"""

# Third party imports
from decouple import config

# Local application imports
from .base_settings import *

# Per Django security warning, debug is turned off for production!
DEBUG = False

ALLOWED_HOSTS = ["0.0.0.0"]  # For running production environment locally with docker

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_NAME"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": "postgres_database",  # Name of the docker service running postgres
        "PORT": 5432,  # Default postgres port
    }
}
