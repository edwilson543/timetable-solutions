"""
Operations on the User and Profile model.
"""

# Django imports
from django.contrib.auth import models as auth_models
from django.db import transaction

# Local application imports
from data import constants


def update_user(
    user: auth_models.User,
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    approved_by_school_admin: bool | None = None,
    role: constants.UserRole | None = None
) -> auth_models.User:
    """
    Update a user's details on the User or Profile model as relevant.
    """
    profile = user.profile
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if email is not None:
        user.email = email
    if role is not None:
        profile.role = role
    if approved_by_school_admin is not None:
        profile.approved_by_school_admin = approved_by_school_admin

    with transaction.atomic():
        profile.save()
        user.save()

    return user


def delete_user(user: auth_models.User) -> tuple:
    """
    Delete a user from the db. Note this also deletes their profile.
    """
    return user.delete()
