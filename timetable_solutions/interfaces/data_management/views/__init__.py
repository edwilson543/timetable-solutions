"""
All views relating to the data upload page
"""
from .data_upload_page import UploadPage
from .download_views import (
    BreakDownload,
    ClassroomDownload,
    LessonDownload,
    PupilDownload,
    TeacherDownload,
    TimetableDownload,
    YearGroupDownload,
)
from .reset_views import (
    AllSchoolDataReset,
    BreakReset,
    ClassroomListReset,
    LessonReset,
    PupilListReset,
    TeacherListReset,
    TimetableStructureReset,
    YearGroupReset,
)
from .teacher import (
    TeacherCreate,
    TeacherLanding,
    TeacherSearch,
    TeacherUpdate,
    TeacherUpload,
)
from .upload_views import (
    BreaksUpload,
    ClassroomListUpload,
    LessonsUpload,
    PupilListUpload,
    TeacherListUpload,
    TimetableStructureUpload,
    YearGroupListUpload,
)
