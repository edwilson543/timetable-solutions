"""
All views relating to the data upload page
"""
from .data_upload_page import UploadPage
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
    TeacherExampleDownload,
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
