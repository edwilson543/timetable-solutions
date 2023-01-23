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
from data import constants
from data import models
from tests import factories


@pytest.mark.django_db
class TestTeacher:

    # --------------------
    # Factories tests
    # --------------------

    def test_create_new_valid_teacher(self):
        """
        Tests that we can create and save a Teacher via the create_new method
        """
        # Make a school for the teacher to teach at
        school = factories.School()

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
        teacher = factories.Teacher()

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
        teacher = factories.Teacher()

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
        lesson = factories.Lesson()
        assert lesson.teacher

        # Try deleting all the lessons for a school
        with pytest.raises(ProtectedError):
            models.Teacher.delete_all_instances_for_school(
                school_id=lesson.school.school_access_key
            )

    # --------------------
    # Queries tests
    # --------------------

    def test_check_if_busy_at_time_of_timeslot_when_teacher_is_busy_at_passed_slot(
        self,
    ):
        """Test that a teacher is busy if they're teaching at the exact passed lesson slot"""
        # Make a teacher who teaches a lesson fixed at some slot
        teacher = factories.Teacher()
        slot = factories.TimetableSlot(school=teacher.school)
        factories.Lesson(
            school=teacher.school, teacher=teacher, user_defined_time_slots=(slot,)
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
        teacher = factories.Teacher()
        busy_slot = factories.TimetableSlot(school=teacher.school)
        factories.Lesson(
            school=teacher.school, teacher=teacher, user_defined_time_slots=(busy_slot,)
        )

        # Make another slot with the exact same times (and day) to check business against
        check_slot = factories.TimetableSlot(
            school=teacher.school,
            day_of_week=busy_slot.day_of_week,
            period_starts_at=busy_slot.period_starts_at,
            period_ends_at=busy_slot.period_ends_at,
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
        teacher = factories.Teacher()
        busy_slot = factories.TimetableSlot(
            school=teacher.school,
            period_starts_at=dt.time(hour=9),
            period_ends_at=dt.time(hour=10),
        )
        factories.Lesson(
            school=teacher.school, teacher=teacher, user_defined_time_slots=(busy_slot,)
        )

        # Make another slot with overlapping times (and same day) to check business against
        check_slot = factories.TimetableSlot(
            school=teacher.school,
            day_of_week=busy_slot.day_of_week,
            period_starts_at=dt.time(hour=9, minute=30),
            period_ends_at=dt.time(hour=10, minute=30),
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
        teacher = factories.Teacher()
        busy_slot = factories.TimetableSlot(
            school=teacher.school, day_of_week=constants.Day.MONDAY
        )
        factories.Lesson(
            school=teacher.school, teacher=teacher, user_defined_time_slots=(busy_slot,)
        )

        # Make another slot, which has a different day
        check_slot = factories.TimetableSlot(
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
        lesson = factories.Lesson()
        teacher = lesson.teacher

        # Execute test unit
        n_lessons = teacher.get_lessons_per_week()

        # Since this is the teacher's only lesson, they should just have the factory lesson to teach
        assert n_lessons == lesson.total_required_slots
