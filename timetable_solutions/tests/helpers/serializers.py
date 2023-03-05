"""
Helpers for dealing with serialized data.
These are used when testing for the expected serialized content of some test subject.
"""

# Standard library imports
from collections import OrderedDict

# Local application imports
from data import models
from interfaces.constants import UrlName


def expected_teacher(teacher: models.Teacher) -> OrderedDict:
    """Get the expected serialized data from a single teacher."""
    return OrderedDict(
        [
            ("teacher_id", teacher.teacher_id),
            ("firstname", teacher.firstname),
            ("surname", teacher.surname),
            ("title", teacher.title),
            ("update_url", UrlName.TEACHER_UPDATE.url(teacher_id=teacher.teacher_id)),
        ]
    )
