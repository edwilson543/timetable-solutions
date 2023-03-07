"""Exceptions relating to year group data management."""


class CouldNotCreateYearGroup(Exception):
    """Raised if a year group cannot be created in the database."""

    pass


class CouldNotUpdateYearGroup(Exception):
    """Raised if a year group cannot be updated in the database."""

    pass


class CouldNotDeleteYearGroup(Exception):
    """Raised if a year group cannot be deleted in the database."""

    pass
