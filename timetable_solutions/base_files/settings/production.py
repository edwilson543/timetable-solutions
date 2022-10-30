"""
Settings specific to the production environment.
python-decouple's config is used extensively to retrieve environment variables.
"""

# Third party imports
from decouple import config

# Local application imports
from .base_settings import *

# Per Django security warning, debug is turned off for production!
DEBUG = False

ALLOWED_HOSTS = ["0.0.0.0"]  # For running production environment locally with docker

SECRET_KEY = config("SECRET_KEY")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_NAME"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": "172.20.0.2",  # Default postgres localhost port
        "PORT": 5432,  # Default postgres port
    }
}
