"""
Convenience imports. Within the interfaces layer we simply import data_management.
"""

# Standard library imports
from typing import Union

# Local application imports
# File upload processors
from domain.data_management.upload_processors._break import BreakFileUploadProcessor
from domain.data_management.upload_processors._lesson import LessonFileUploadProcessor
from domain.data_management.upload_processors._other_models import (
    ClassroomFileUploadProcessor,
    TeacherFileUploadProcessor,
    YearGroupFileUploadProcessor,
)
from domain.data_management.upload_processors._pupil import PupilFileUploadProcessor
from domain.data_management.upload_processors._timetable_slot import (
    TimetableSlotFileUploadProcessor,
)

# Type hints
Processor = Union[
    TeacherFileUploadProcessor,
    ClassroomFileUploadProcessor,
    YearGroupFileUploadProcessor,
    PupilFileUploadProcessor,
    TimetableSlotFileUploadProcessor,
    LessonFileUploadProcessor,
    BreakFileUploadProcessor,
]
