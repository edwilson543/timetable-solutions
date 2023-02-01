"""
Convenience imports. Within the interfaces layer we simply import data_upload_processing.
"""
from typing import Union

# File upload processors
from domain.data_upload_processing.processors._other_models import (
    TeacherFileUploadProcessor,
    ClassroomFileUploadProcessor,
    YearGroupFileUploadProcessor,
    PupilFileUploadProcessor,
)
from domain.data_upload_processing.processors._timetable_slot import (
    TimetableSlotFileUploadProcessor,
)
from domain.data_upload_processing.processors._lesson import (
    LessonFileUploadProcessor,
)
from domain.data_upload_processing.processors._break import (
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
]
