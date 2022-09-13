"""Utility functions / classes / typehints relating to data models"""


# TYPE HINTS
from typing import TypeVar

from django.db.models import Model

ModelSubclass = TypeVar("ModelSubclass", bound=Model)  # Typehint when referring to specific django Model subclasses
