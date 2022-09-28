"""Settings specific to the aws production environment"""

# Standard library imports
import os

# Local application imports
from .base_settings import *

# Per django security warning, the secret key is loaded in from an environment variable
# The SECRET_KEY environment variable has been set on the elastic beanstalk environment
SECRET_KEY = os.environ.get("SECRET_KEY")

# Per Django security warning, debug is turned off for production!
DEBUG = False

ALLOWED_HOSTS = ["timetable-solutions.eu-west-2.elasticbeanstalk.com"]

DATABASES = {}  # TODO
