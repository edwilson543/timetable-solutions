"""
Convenience imports. Within the interfaces layer we simply import data_upload_processing.
"""
from typing import Union

from .constants import FileStructure, UploadFileStructure
from .file_upload_processor import FileUploadProcessor
from .lesson_file_upload_processor import LessonFileUploadProcessor
from .upload_status_tracking import (
    UploadStatusTracker,
    UploadStatus,
    UploadStatusReason,
)
from .reset_uploads import ResetUploads, ResetWarning


# Type hints
Processor = Union[FileUploadProcessor, LessonFileUploadProcessor]
