"""
Convenience imports. Within the interfaces layer we simply import data_upload_processing.
"""
from typing import Union

from .lesson_file_upload_processor import LessonFileUploadProcessor
from .file_upload_processors import (
    TeacherFileUploadProcessor,
    ClassroomFileUploadProcessor,
    YearGroupFileUploadProcessor,
    PupilFileUploadProcessor,
    TimetableFileUploadProcessor,
)
from .upload_status_tracking import (
    UploadStatusTracker,
    UploadStatus,
    UploadStatusReason,
)
from .reset_uploads import ResetUploads, ResetWarning


# Type hints
Processor = Union[
    TeacherFileUploadProcessor,
    ClassroomFileUploadProcessor,
    YearGroupFileUploadProcessor,
    PupilFileUploadProcessor,
    TimetableFileUploadProcessor,
    LessonFileUploadProcessor,
]
