"""
Convenience imports. Within the interfaces layer we simply import data_management.
"""
from typing import Union

# File upload processors
from domain.data_management.upload_processors._other_models import (
    TeacherFileUploadProcessor,
    ClassroomFileUploadProcessor,
    YearGroupFileUploadProcessor,
)
from domain.data_management.upload_processors._pupil import PupilFileUploadProcessor
from domain.data_management.upload_processors._timetable_slot import (
    TimetableSlotFileUploadProcessor,
)
from domain.data_management.upload_processors._lesson import (
    LessonFileUploadProcessor,
)
from domain.data_management.upload_processors._break import (
    BreakFileUploadProcessor,
)

# Upload status tracking
from .upload_status_tracking import (
    UploadStatusTracker,
    UploadStatus,
    UploadStatusReason,
)

# Upload resetting
from .reset_uploads import ResetUploads, ResetWarning


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
