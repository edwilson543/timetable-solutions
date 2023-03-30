"""
Exceptions classes raised by the data layer.
"""


class SchoolMismatchError(Exception):
    """
    Raise when trying to relate to data items from different schools.
    e.g. assigning a teacher from one school to a lesson from another.

    This is enforced in the data layer since contamination between
    school's data is very undesirable and should never be committed to
    the database.
    """

    pass
