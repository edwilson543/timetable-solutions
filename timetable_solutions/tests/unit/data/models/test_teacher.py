"""
Unit tests for methods on the Teacher class
"""


# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Django imports
from django.db import IntegrityError
from django.db.models import ProtectedError

# Local application imports
from data import constants, models
from tests import data_factories


@pytest.mark.django_db
class TestTeacherFactories:
    def test_create_new_valid_teacher(self):
        """
        Tests that we can create and save a Teacher via the create_new method
        """
        # Make a school for the teacher to teach at
        school = data_factories.School()

        # Try creating teacher using create_new
        teacher = models.Teacher.create_new(
            school_id=school.school_access_key,
            teacher_id=1,
            firstname="test",
            surname="test",
            title="mr",
        )

        # Check teacher was created
        all_teachers = models.Teacher.objects.all()
        assert all_teachers.count() == 1
        assert all_teachers.first() == teacher

    def test_create_new_fails_when_teacher_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Teachers with the same id / school, due to unique_together on the Meta class
        """
        # Make a teacher to occupy an id value
        teacher = data_factories.Teacher()

        # Try making a teacher with the same school / id
        with pytest.raises(IntegrityError):
            models.Teacher.create_new(
                school_id=teacher.school.school_access_key,
                teacher_id=teacher.teacher_id,
                firstname="test-2",
                surname="test-2",
                title="mrs",
            )

    def test_delete_all_instances_for_school_successful_when_no_lessons(self):
        """
        Test that we can successfully delete all teachers associated with a school, when there are no Lessons
        instances referencing the teachers as foreign keys.
        """
        # Get a teacher
        teacher = data_factories.Teacher()

        # Delete all the teachers at this teacher's school
        outcome = models.Teacher.delete_all_instances_for_school(
            school_id=teacher.school.school_access_key
        )

        # Check outcome
        deleted_ref = outcome[1]
        assert deleted_ref["data.Teacher"] == 1

        all_teachers = models.Teacher.objects.all()
        assert all_teachers.count() == 0

    def test_delete_all_instances_for_school_unsuccessful_when_attached_to_lessons(
        self,
    ):
        """
        Test that we cannot delete all teachers associated with a school, when there is at least one Lesson
        referencing the teachers we are trying to delete.
        """
        # Make a lesson with a teacher
        lesson = data_factories.Lesson()
        assert lesson.teacher

        # Try deleting all the lessons for a school
        with pytest.raises(ProtectedError):
            models.Teacher.delete_all_instances_for_school(
                school_id=lesson.school.school_access_key
            )


@pytest.mark.django_db
class TestTeacherMutators:
    @pytest.mark.parametrize("firstname", ["testname", None])
    @pytest.mark.parametrize("surname", ["testnameson", None])
    @pytest.mark.parametrize("title", ["mr", None])
    def test_update_updates_teacher_details_with_params(
        self, firstname: str, surname: str, title: str
    ):
        teacher = data_factories.Teacher()

        teacher.update(firstname=firstname, surname=surname, title=title)

        expected_firstname = firstname or teacher.firstname
        expected_surname = surname or teacher.surname
        expected_title = title or teacher.title

        teacher.refresh_from_db()

        assert teacher.firstname == expected_firstname
        assert teacher.surname == expected_surname
        assert teacher.title == expected_title


@pytest.mark.django_db
class TestTeacherQueries:
    def test_check_if_busy_at_time_of_timeslot_when_teacher_in_lesson_at_passed_slot(
        self,
    ):
        """Test that a teacher is busy if they're teaching at the exact passed lesson slot"""
        # Make a teacher who teaches a lesson fixed at some slot
        teacher = data_factories.Teacher()
        slot = data_factories.TimetableSlot(school=teacher.school)
        data_factories.Lesson(
            school=teacher.school, teacher=teacher, user_defined_time_slots=(slot,)
        )

        # Call test function
        is_busy = teacher.check_if_busy_at_time_of_timeslot(slot=slot)

        # Check teacher successfully made busy
        assert is_busy

    def test_check_if_busy_at_time_of_timeslot_when_teacher_in_break_at_passed_slot(
        self,
    ):
        """Test that a teacher is busy if they're on a break at the exact passed lesson slot"""
        # Make a teacher who teaches a lesson fixed at some slot
        teacher = data_factories.Teacher()
        slot = data_factories.TimetableSlot(school=teacher.school)
        data_factories.Break(
            school=teacher.school,
            teachers=models.Teacher.objects.filter(pk=teacher.pk),
            day_of_week=slot.day_of_week,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
        )

        # Call test function
        is_busy = teacher.check_if_busy_at_time_of_timeslot(slot=slot)

        # Check teacher successfully made busy
        assert is_busy

    def test_check_if_busy_at_time_of_timeslot_when_teacher_is_busy_at_exact_times_of_passed_slot(
        self,
    ):
        """
        Test that a teacher is busy if they're teaching at another slot with
        the exact same times as the passed slot
        """
        # Make a teacher who teaches a lesson fixed at some slot
        teacher = data_factories.Teacher()
        busy_slot = data_factories.TimetableSlot(school=teacher.school)
        data_factories.Lesson(
            school=teacher.school, teacher=teacher, user_defined_time_slots=(busy_slot,)
        )

        # Make another slot with the exact same times (and day) to check business against
        check_slot = data_factories.TimetableSlot(
            school=teacher.school,
            day_of_week=busy_slot.day_of_week,
            starts_at=busy_slot.starts_at,
            ends_at=busy_slot.ends_at,
        )

        # Call test function
        is_busy = teacher.check_if_busy_at_time_of_timeslot(slot=check_slot)

        # Check teacher successfully made busy
        assert is_busy

    def test_check_if_busy_at_time_of_timeslot_partially_overlapping_timeslot(self):
        """
        Test that a teacher is busy if they're teaching at another slot with
        slightly overlapping slots
        """
        # Make a teacher who teaches a lesson fixed at some slot
        teacher = data_factories.Teacher()
        busy_slot = data_factories.TimetableSlot(
            school=teacher.school,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
        )
        data_factories.Lesson(
            school=teacher.school, teacher=teacher, user_defined_time_slots=(busy_slot,)
        )

        # Make another slot with overlapping times (and same day) to check business against
        check_slot = data_factories.TimetableSlot(
            school=teacher.school,
            day_of_week=busy_slot.day_of_week,
            starts_at=dt.time(hour=9, minute=30),
            ends_at=dt.time(hour=10, minute=30),
        )

        # Call test function
        is_busy = teacher.check_if_busy_at_time_of_timeslot(slot=check_slot)

        # Check teacher successfully made busy
        assert is_busy

    def test_check_if_busy_at_time_of_timeslot_when_teacher_is_not_busy(self):
        """Test that the check_if_busy_at_time_slot method returns 'False' when we expect it to"""
        # Make a teacher who teaches a lesson fixed at some slot
        # The business isn't really necessary, but ensures teaching one lesson doesn't
        # make the teacher constantly 'busy'
        teacher = data_factories.Teacher()
        busy_slot = data_factories.TimetableSlot(
            school=teacher.school, day_of_week=constants.Day.MONDAY
        )
        data_factories.Lesson(
            school=teacher.school, teacher=teacher, user_defined_time_slots=(busy_slot,)
        )

        # Make another slot, which has a different day
        check_slot = data_factories.TimetableSlot(
            school=teacher.school, day_of_week=constants.Day.TUESDAY
        )

        # Call test function
        is_busy = teacher.check_if_busy_at_time_of_timeslot(slot=check_slot)

        # Check teacher successfully made busy
        assert not is_busy

    def test_get_lessons_per_week(self):
        """
        Test that the correct number of lessons per week is retrieved for a teacher.
        """
        # Make a lesson (& teacher)
        lesson = data_factories.Lesson()
        teacher = lesson.teacher

        # Execute test unit
        n_lessons = teacher.get_lessons_per_week()

        # Since this is the teacher's only lesson, they should just have the factory lesson to teach
        assert n_lessons == lesson.total_required_slots
