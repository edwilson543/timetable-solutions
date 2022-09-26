"""Settings specific to the aws production environment"""

# Third party imports
from decouple import config

# Local application imports
from .base_settings import *

# Per django security warning, the secret key is loaded in from an environment variable
SECRET_KEY = config("SECRET_KEY")

# Per Django security warning, debug is turned off for production!
DEBUG = False

ALLOWED_HOSTS = []  # TODO add domain name

DATABASES = {}  # TODO
