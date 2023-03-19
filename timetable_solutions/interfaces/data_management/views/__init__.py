"""
All views relating to data management.
"""

from .classroom import (
    ClassroomCreate,
    ClassroomExampleDownload,
    ClassroomLanding,
    ClassroomSearch,
    ClassroomUpdate,
    ClassroomUpload,
)
from .pupil import (
    PupilCreate,
    PupilExampleDownload,
    PupilLanding,
    PupilSearch,
    PupilUpdate,
    PupilUpload,
)
from .teacher import (
    TeacherCreate,
    TeacherExampleDownload,
    TeacherLanding,
    TeacherSearch,
    TeacherUpdate,
    TeacherUpload,
)
from .timetable_slot import (
    TimetableSlotCreate,
    TimetableSlotExampleDownload,
    TimetableSlotLanding,
    TimetableSlotSearch,
    TimetableSlotUpdateTimings,
    TimetableSlotUpload,
)
from .year_group import (
    YearGroupCreate,
    YearGroupExampleDownload,
    YearGroupLanding,
    YearGroupList,
    YearGroupUpdate,
    YearGroupUpload,
)
