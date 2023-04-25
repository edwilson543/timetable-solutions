"""
All views relating to data management.
"""

from .break_ import (
    BreakCreate,
    BreakExampleDownload,
    BreakLanding,
    BreakSearch,
    BreakUpdate,
    BreakUpdateRelatedTeachersPartial,
    BreakUpload,
)
from .classroom import (
    ClassroomCreate,
    ClassroomExampleDownload,
    ClassroomLanding,
    ClassroomLessonsPartial,
    ClassroomSearch,
    ClassroomUpdate,
    ClassroomUpload,
)
from .lesson import (
    LessonCreate,
    LessonExampleDownload,
    LessonLanding,
    LessonSearch,
    LessonUpdate,
    LessonUpdatePupilsPartial,
    LessonUpdateUserDefinedTimetableSlotPartial,
    LessonUpload,
)
from .pupil import (
    PupilCreate,
    PupilExampleDownload,
    PupilLanding,
    PupilLessonsPartial,
    PupilSearch,
    PupilUpdate,
    PupilUpload,
)
from .teacher import (
    TeacherCreate,
    TeacherExampleDownload,
    TeacherLanding,
    TeacherLessonsPartial,
    TeacherSearch,
    TeacherUpdate,
    TeacherUpload,
)
from .timetable_slot import (
    TimetableSlotCreate,
    TimetableSlotExampleDownload,
    TimetableSlotLanding,
    TimetableSlotSearch,
    TimetableSlotUpdate,
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
