"""Tests for serializer classes for the basic school data models."""

# Standard library imports
import datetime as dt
from collections import OrderedDict
from unittest import mock

# Third party imports
import pytest

# Local application imports
from interfaces.constants import UrlName
from interfaces.data_management import serializers
from tests import data_factories
from tests.helpers import serializers as serializers_helpers


@pytest.mark.django_db
class TestYearGroupSerializer:
    def test_serialize_individual_instance_no_pupils(self):
        year_group = data_factories.YearGroup()

        serialized_year_group = serializers.YearGroup(year_group).data

        assert serialized_year_group == serializers_helpers.expected_year_group(
            year_group
        )

    def test_serialize_individual_instance_with_pupils(self):
        pupil = data_factories.Pupil()
        year_group = pupil.year_group

        serialized_year_group = serializers.YearGroup(year_group).data

        assert serialized_year_group == serializers_helpers.expected_year_group(
            year_group
        )

    def test_serialize_multiple_year_groups(self):
        yg_a = data_factories.YearGroup()
        yg_b = data_factories.YearGroup()

        serialized_year_groups = serializers.YearGroup([yg_a, yg_b], many=True).data

        assert serialized_year_groups == [
            serializers_helpers.expected_year_group(yg_a),
            serializers_helpers.expected_year_group(yg_b),
        ]


@pytest.mark.django_db
class TestLessonSerializer:
    def test_serialize_individual_instance(self):
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        pupil = data_factories.Pupil(school=school, year_group=yg)
        lesson = data_factories.Lesson(school=school, pupils=(pupil,))

        serialized_lesson = serializers.Lesson(lesson).data

        assert serialized_lesson == OrderedDict(
            [
                ("lesson_id", lesson.lesson_id),
                ("subject_name", lesson.subject_name),
                ("year_group", yg.year_group_name),
                ("teacher", f"{lesson.teacher.title} {lesson.teacher.surname}"),
                (
                    "classroom",
                    f"{lesson.classroom.building} {lesson.classroom.room_number}",
                ),
                ("total_required_slots", lesson.total_required_slots),
            ]
        )

    def test_serialize_multiple_lessons(self):
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        pupil = data_factories.Pupil(school=school, year_group=yg)
        lesson_a = data_factories.Lesson(school=school, pupils=(pupil,))
        lesson_b = data_factories.Lesson(school=school, pupils=(pupil,))

        serialized_lessons = serializers.Lesson([lesson_a, lesson_b], many=True).data

        assert serialized_lessons == [
            OrderedDict(
                [
                    ("lesson_id", lesson_a.lesson_id),
                    ("subject_name", lesson_a.subject_name),
                    ("year_group", yg.year_group_name),
                    ("teacher", f"{lesson_a.teacher.title} {lesson_a.teacher.surname}"),
                    (
                        "classroom",
                        f"{lesson_a.classroom.building} {lesson_a.classroom.room_number}",
                    ),
                    ("total_required_slots", lesson_a.total_required_slots),
                ]
            ),
            OrderedDict(
                [
                    ("lesson_id", lesson_b.lesson_id),
                    ("subject_name", lesson_b.subject_name),
                    ("year_group", yg.year_group_name),
                    ("teacher", f"{lesson_b.teacher.title} {lesson_b.teacher.surname}"),
                    (
                        "classroom",
                        f"{lesson_b.classroom.building} {lesson_b.classroom.room_number}",
                    ),
                    ("total_required_slots", lesson_b.total_required_slots),
                ]
            ),
        ]


@pytest.mark.django_db
class TestTeacherSerializer:
    def test_serialize_individual_instance(self):
        teacher = data_factories.Teacher()

        serialized_teacher = serializers.Teacher(teacher).data

        assert serialized_teacher == serializers_helpers.expected_teacher(teacher)

    @mock.patch.object(
        serializers.school_solver_queries,
        "check_school_has_timetable_solutions",
        return_value=True,
    )
    def test_serialize_individual_instance_with_timetable_includes_timetable_url(
        self, mock_has_solutions: mock.Mock
    ):
        teacher = data_factories.Teacher()

        serialized_teacher = serializers.Teacher(teacher).data

        assert serialized_teacher["timetable_url"] == UrlName.TEACHER_TIMETABLE.url(
            teacher_id=teacher.teacher_id
        )

    def test_serialize_individual_instance_with_lesson(self):
        lesson = data_factories.Lesson.with_n_pupils()
        teacher = lesson.teacher

        serialized_teacher = serializers.Teacher(teacher).data

        assert serialized_teacher == serializers_helpers.expected_teacher(teacher)

    def test_serialize_multiple_teachers(self):
        teacher_a = data_factories.Teacher()
        teacher_b = data_factories.Teacher()

        serialized_teacher = serializers.Teacher([teacher_a, teacher_b], many=True).data

        assert serialized_teacher == [
            serializers_helpers.expected_teacher(teacher_a),
            serializers_helpers.expected_teacher(teacher_b),
        ]


@pytest.mark.django_db
class TestClassroomSerializer:
    def test_serialize_individual_instance(self):
        classroom = data_factories.Classroom()

        serialized_classroom = serializers.Classroom(classroom).data

        assert serialized_classroom == serializers_helpers.expected_classroom(classroom)

    def test_serialize_individual_instance_with_lesson(self):
        lesson = data_factories.Lesson.with_n_pupils()
        classroom = lesson.classroom

        serialized_classroom = serializers.Classroom(classroom).data

        assert serialized_classroom == serializers_helpers.expected_classroom(classroom)

    def test_serialize_multiple_classrooms(self):
        classroom_a = data_factories.Classroom()
        classroom_b = data_factories.Classroom()

        serialized_classrooms = serializers.Classroom(
            [classroom_a, classroom_b], many=True
        ).data

        assert serialized_classrooms == [
            serializers_helpers.expected_classroom(classroom_a),
            serializers_helpers.expected_classroom(classroom_b),
        ]


@pytest.mark.django_db
class TestPupilSerializer:
    def test_serialize_individual_instance(self):
        pupil = data_factories.Pupil()

        serialized_pupil = serializers.Pupil(pupil).data

        assert serialized_pupil == serializers_helpers.expected_pupil(pupil)

    def test_serialize_multiple_pupils(self):
        pupil_a = data_factories.Pupil()
        pupil_b = data_factories.Pupil()

        serialized_pupils = serializers.Pupil([pupil_a, pupil_b], many=True).data

        assert serialized_pupils == [
            serializers_helpers.expected_pupil(pupil_a),
            serializers_helpers.expected_pupil(pupil_b),
        ]


@pytest.mark.django_db
class TestTimetableSlotSerializer:
    @pytest.mark.parametrize(
        "starts_at,ends_at",
        [
            (dt.time(hour=8), dt.time(hour=8, minute=45)),
            (dt.time(hour=17), dt.time(hour=18)),
        ],
    )
    def test_serialize_individual_instance(self, starts_at: dt.time, ends_at: dt.time):
        slot = data_factories.TimetableSlot(starts_at=starts_at, ends_at=ends_at)

        serialized_slot = serializers.TimetableSlot(slot).data

        assert serialized_slot == serializers_helpers.expected_slot(slot)

    def test_serialize_multiple_slots(self):
        slot_a = data_factories.TimetableSlot()
        slot_b = data_factories.TimetableSlot()

        serialized_slots = serializers.TimetableSlot([slot_a, slot_b], many=True).data

        assert serialized_slots == [
            serializers_helpers.expected_slot(slot_a),
            serializers_helpers.expected_slot(slot_b),
        ]


@pytest.mark.django_db
class TestBreakSerializer:
    @pytest.mark.parametrize(
        "starts_at,ends_at",
        [
            (dt.time(hour=8), dt.time(hour=8, minute=45)),
            (dt.time(hour=17), dt.time(hour=18)),
        ],
    )
    def test_serialize_individual_instance(self, starts_at: dt.time, ends_at: dt.time):
        break_ = data_factories.Break(starts_at=starts_at, ends_at=ends_at)

        serialized_break = serializers.Break(break_).data

        assert serialized_break == serializers_helpers.expected_break(break_)

    def test_serialize_multiple_breaks(self):
        break_a = data_factories.Break()
        break_b = data_factories.Break()

        serialized_breaks = serializers.Break([break_a, break_b], many=True).data

        assert serialized_breaks == [
            serializers_helpers.expected_break(break_a),
            serializers_helpers.expected_break(break_b),
        ]
