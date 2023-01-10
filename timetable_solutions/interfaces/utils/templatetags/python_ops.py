"""
Module defining some basic python operations for use in django templates.
"""

# Standard library imports
from typing import Mapping, Protocol, TypeVar

# Django imports
from django import template


register = template.Library()


class Addable(Protocol):
    """Protocol for any objects that can be added together"""

    def __add__(self, other: "Addable") -> "Addable":
        ...


@register.simple_tag(name="add")
def add(x: Addable, y: Addable) -> Addable:
    """
    Implement python addition for integers, floats and strings.
    """
    return x + y


K = TypeVar("K")
V = TypeVar("V")


@register.simple_tag(name="get_item")
def get_item(mapping: Mapping[K, V], key: K) -> V | None:
    """
    Implement mapping indexing for django template.
    """
    return mapping.get(key)
