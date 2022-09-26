"""Settings specific to the aws production environment"""
from .base_settings import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ""  # TODO

# Per Django security warning, debug is turned off for production!
DEBUG = False

ALLOWED_HOSTS = []  # TODO add domain name

DATABASES = {}  # TODO
