from .base_forms import BulkUpload
from .break_ import (
    BreakAddTeacher,
    BreakCreate,
    BreakSearch,
    BreakUpdateTimings,
    BreakUpdateYearGroups,
)
from .classroom import ClassroomCreate, ClassroomSearch, ClassroomUpdate
from .lesson import (
    LessonAddPupil,
    LessonAddUserDefinedTimetableSlot,
    LessonCreate,
    LessonSearch,
    LessonUpdate,
)
from .pupil import PupilCreate, PupilSearch, PupilUpdate
from .teacher import TeacherCreate, TeacherSearch, TeacherUpdate
from .timetable_slot import (
    TimetableSlotCreate,
    TimetableSlotSearch,
    TimetableSlotUpdateTimings,
    TimetableSlotUpdateYearGroups,
)
from .year_group import YearGroupCreate, YearGroupUpdate
