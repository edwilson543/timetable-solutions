"""
Settings specific to the local development environment
"""

# Django imports
from django.contrib import messages

# Local application imports
from .base_settings import *


# Basic django settings
ALLOWED_HOSTS = ['.localhost', '127.0.0.1', '[::1]', '0.0.0.0']

DEBUG = True

MESSAGE_LEVEL = messages.DEBUG

SECRET_KEY = 'django-insecure-&b(x7(hn8==(696kz$y9hb!l_=1tuq)#j@-9(1sk9gy=1^nopa'


# Database settings -> sqlite in development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Custom settings
ENABLE_REST_API = True
