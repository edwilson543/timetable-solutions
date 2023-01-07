"""
Convenience imports. Within the interfaces layer we simply import data_upload_processing.
"""
from typing import Union

# File upload processors
from domain.data_upload_processing.processors.other_upload_processors import (
    TeacherFileUploadProcessor,
    ClassroomFileUploadProcessor,
    YearGroupFileUploadProcessor,
    PupilFileUploadProcessor,
)
from .processors.timetable_slot_upload_processor import TimetableSlotFileUploadProcessor
from domain.data_upload_processing.processors.lesson_upload_processor import (
    LessonFileUploadProcessor,
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
]
