"""Exceptions relating to classroom data management."""


class CouldNotCreateClassroom(Exception):
    """Raised if a classroom cannot be created in the database."""

    pass


class CouldNotUpdateClassroom(Exception):
    """Raised if a classroom cannot be updated in the database."""

    pass
