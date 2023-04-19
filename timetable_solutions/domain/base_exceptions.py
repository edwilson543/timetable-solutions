"""
Base exceptions arising from failed domain operations.
Each model implements its own exceptions, including subclasses of these.
"""


class _OperationError(Exception):
    """
    Operation error with a human friendly error message.
    """

    def __init__(self, human_error_message: str) -> None:
        super().__init__(human_error_message)
        self.human_error_message = human_error_message


class UnableToCreateModelInstance(_OperationError):
    """
    Raise if some model instance cannot be created in the database.
    """

    pass


class UnableToUpdateModelInstance(_OperationError):
    """
    Raise if some model instance cannot be updated in the database.
    """

    pass


class UnableToDeleteModelInstance(_OperationError):
    """
    Raise if some model instance cannot be deleted from the database.
    """

    pass
