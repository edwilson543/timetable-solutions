"""Exceptions relating to teacher data management."""


class CouldNotCreateTeacher(Exception):
    """Raised if a teacher cannot be created in the database."""

    pass


class CouldNotUpdateTeacher(Exception):
    """Raised if a teacher cannot be updated in the database."""

    pass


class CouldNotDeleteTeacher(Exception):
    """Raised if a teacher cannot be deleted in the database."""

    pass
