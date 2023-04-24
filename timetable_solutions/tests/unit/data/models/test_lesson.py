"""
Unit tests for the Lesson model and its manager, LessonQuerySet.
"""

# Third party imports
import pytest

# Django imports
from django.db import IntegrityError

# Local application imports
from data import constants, models
from tests import data_factories


@pytest.mark.django_db
class TestLessonQuerySet:
    """
    Unit tests for the LessonQuerySet.
    """

    def test_get_lessons_requiring_solving(self):
        """
        Check that the correct subset of lessons is extracted for the solver.
        """
        # Make one lesson requiring solving...
        school = data_factories.School()
        unsolved_lesson = data_factories.Lesson(school=school, total_required_slots=1)

        # ...and one lesson not requiring solving
        solved_slot = data_factories.TimetableSlot(school=school)
        data_factories.Lesson(
            school=school,
            total_required_slots=1,
            user_defined_time_slots=(solved_slot,),
        )

        # Filter by the lessons requiring solving
        lessons_needing_solving = models.Lesson.objects.get_lessons_requiring_solving(
            school_id=school.school_access_key
        )

        # Check only unsolved lesson is in the lessons needing solving
        assert lessons_needing_solving.count() == 1
        assert lessons_needing_solving.first() == unsolved_lesson
        # Therefore we have that the other lesson doesn't need solving


@pytest.mark.django_db
class TestCreateNewLesson:
    def test_create_new_valid_lesson(self):
        # Get some data to make the lesson with
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)
        classroom = data_factories.Classroom(school=school)
        pupil = data_factories.Pupil(school=school)
        user_defined_slot = data_factories.TimetableSlot(
            school=school, relevant_year_groups=(pupil.year_group,)
        )

        # Try creating the lesson
        lesson = models.Lesson.create_new(
            school_id=school.school_access_key,
            lesson_id="test",
            subject_name="test",
            total_required_slots=4,
            total_required_double_periods=2,
            teacher=teacher,
            classroom=classroom,
            pupils=models.Pupil.objects.all(),
            year_group=pupil.year_group,
            user_defined_time_slots=models.TimetableSlot.objects.all(),
        )

        # Check lesson was created
        assert models.Lesson.objects.get() == lesson

        # Check lesson fields are as expected
        assert lesson.school == school
        assert lesson.teacher == teacher
        assert lesson.classroom == classroom
        assert lesson.pupils.get() == pupil
        assert lesson.year_group == pupil.year_group
        assert user_defined_slot in lesson.user_defined_time_slots.all()

    def test_create_new_raises_when_lesson_id_not_unique_for_school(self):
        # Make a lesson to block uniqueness
        lesson = data_factories.Lesson()

        # Try creating another lesson with the same id / school
        with pytest.raises(IntegrityError):
            models.Lesson.create_new(
                school_id=lesson.school.school_access_key,
                lesson_id=lesson.lesson_id,
                subject_name="test",
                total_required_slots=4,
                total_required_double_periods=2,
            )

    def test_create_new_raises_when_double_periods_exceeds_feasible_amount(self):
        school = data_factories.School()

        with pytest.raises(IntegrityError):
            models.Lesson.create_new(
                school_id=school.school_access_key,
                lesson_id="some-lesson",
                subject_name="some-subject",
                total_required_slots=5,
                total_required_double_periods=3,
            )


@pytest.mark.django_db
class TestLessonDeletionMethods:
    def test_delete_all_lessons_for_school_successful(self):
        """
        Test that we can delete all the lessons associated with a school.
        """
        # Make a lesson
        lesson = data_factories.Lesson()

        # Try deleting the lesson
        models.Lesson.delete_all_lessons_for_school(
            school_id=lesson.school.school_access_key
        )

        # Check lesson was deleted
        all_lessons = models.Lesson.objects.all()
        assert all_lessons.count() == 0

    def test_delete_solver_solution_for_school_successful(self):
        """
        Test that we can delete the solver produced solution for a school.
        """
        # Make a lesson with some solver slots (simulating having been solved)
        school = data_factories.School()
        slot = data_factories.TimetableSlot(school=school)
        lesson = data_factories.Lesson(school=school, solver_defined_time_slots=(slot,))

        # Delete the solver solution for the lesson's school
        models.Lesson.delete_solver_solution_for_school(
            school_id=school.school_access_key
        )

        # Check the lesson no longer has any solver defined time slots
        lesson.refresh_from_db()
        assert lesson.solver_defined_time_slots.count() == 0


@pytest.mark.django_db
class TestAddUserDefinedTimeSlots:
    def test_can_add_time_slot(self):
        slot = data_factories.TimetableSlot()
        lesson = data_factories.Lesson(school=slot.school)

        lesson.add_user_defined_time_slots(models.TimetableSlot.objects.all())

        assert slot in lesson.user_defined_time_slots.all()

    def test_cannot_add_time_slot_when_insufficient_required_slots(self):
        slot = data_factories.TimetableSlot()
        slot = data_factories.TimetableSlot(school=slot.school)
        lesson = data_factories.Lesson(
            school=slot.school, user_defined_time_slots=(slot,), total_required_slots=1
        )

        with pytest.raises(IntegrityError):
            lesson.add_user_defined_time_slots(models.TimetableSlot.objects.all())


@pytest.mark.django_db
class TestAddSolverDefinedTimeSlots:
    def test_can_add_time_slot(self):
        slot = data_factories.TimetableSlot()
        lesson = data_factories.Lesson(school=slot.school)

        lesson.add_solver_defined_time_slots(models.TimetableSlot.objects.all())

        assert slot in lesson.solver_defined_time_slots.all()

    def test_cannot_add_user_defined_time_slot_as_solver_defined(self):
        slot = data_factories.TimetableSlot()
        slot = data_factories.TimetableSlot(school=slot.school)
        lesson = data_factories.Lesson(
            school=slot.school, user_defined_time_slots=(slot,), total_required_slots=2
        )

        with pytest.raises(IntegrityError):
            lesson.add_solver_defined_time_slots(models.TimetableSlot.objects.all())


@pytest.mark.django_db
class TestLessonQueries:
    # --------------------
    # Queries - view timetables logic tests
    # --------------------

    def test_get_all_time_slots_for_lesson_with_user_and_solver_defined_slots(self):
        """
        Test that the get all timeslots method correctly combines the solver / user time slot querysets
        """
        # Make a lesson with both user and solver defined slots
        school = data_factories.School()
        user_defined_slot = data_factories.TimetableSlot(school=school)
        solver_defined_slot = data_factories.TimetableSlot(school=school)
        lesson = data_factories.Lesson(
            school=school,
            user_defined_time_slots=(user_defined_slot,),
            solver_defined_time_slots=(solver_defined_slot,),
        )

        # Get all slots associated with the lesson
        all_slots = lesson.get_all_time_slots()

        # Check all slots includes the user and solver defined slot
        assert all_slots.count() == 2
        assert user_defined_slot in all_slots
        assert solver_defined_slot in all_slots

    # --------------------
    # Queries - solver logic tests
    # --------------------

    def test_get_n_solver_slots_required(self):
        """
        Method to check that the correct number of solver slots is calculated for a lesson
        """
        # Make a lesson with a non-zero delta between defined / required slots
        school = data_factories.School()
        user_defined_slot = data_factories.TimetableSlot(school=school)
        lesson = data_factories.Lesson(
            school=school,
            user_defined_time_slots=(user_defined_slot,),
            total_required_slots=2,
        )

        # Execute test unit
        n_slots = lesson.get_n_solver_slots_required()

        # Check the difference between required / user defined slots has been picked up
        assert n_slots == 1

    def test_get_n_solver_double_periods_required(self):
        """
        Method to check that the correct number of solver double periods is calculated for a lesson
        """
        # Make a lesson with one user-defined double, and one further double required
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)

        slot_1 = data_factories.TimetableSlot(school=school, relevant_year_groups=(yg,))
        slot_2 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_1)

        pupil = data_factories.Pupil(school=school, year_group=yg)
        lesson = data_factories.Lesson(
            school=school,
            user_defined_time_slots=(slot_1, slot_2),  # User defined double
            total_required_double_periods=2,
            total_required_slots=4,
            pupils=(pupil,),
        )

        # Execute test unit
        n_doubles = lesson.get_n_solver_double_periods_required()

        # Check one further double needed from solver
        assert n_doubles == 1

    def test_get_user_defined_double_period_count_on_day_one_double_expected(self):
        """
        Unit test that the method for counting the number of double periods defined by the user for a Lesson
        with ONE double period is correct.
        """
        # Make a lesson with one user-defined double
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)

        slot_1 = data_factories.TimetableSlot(school=school, relevant_year_groups=(yg,))
        slot_2 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_1)

        pupil = data_factories.Pupil(school=school, year_group=yg)
        lesson = data_factories.Lesson(
            school=school,
            user_defined_time_slots=(slot_1, slot_2),  # User defined double
            total_required_slots=4,
            total_required_double_periods=2,
            pupils=(pupil,),
        )

        # Get double period count on Monday and check equal to 1
        double_period_count = lesson.get_user_defined_double_period_count_on_day(
            day_of_week=slot_1.day_of_week
        )

        assert double_period_count == 1

    def test_get_user_defined_double_period_count_on_day_no_doubles_expected(self):
        """
        Unit test that the method for counting the number of double periods defined by the user for a Lesson
        with ZERO double periods is correct.
        """
        # Make a lesson with one double on Tuesday
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)

        slot_1 = data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg,),
            day_of_week=constants.Day.TUESDAY,
        )
        slot_2 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_1)

        pupil = data_factories.Pupil(school=school, year_group=yg)
        lesson = data_factories.Lesson(
            school=school,
            user_defined_time_slots=(slot_1, slot_2),  # User defined double
            total_required_slots=4,
            total_required_double_periods=2,
            pupils=(pupil,),
        )

        # Get doubles on MONDAY - note our doubles are on TUESDAY
        double_period_count = lesson.get_user_defined_double_period_count_on_day(
            day_of_week=constants.Day.MONDAY
        )

        # Check no doubles
        assert double_period_count == 0

    def test_usable_days_year_one_lesson(self):
        """
        Test the correct list of days is returned for a year one lesson.
        """
        # Make a lesson with a slot
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)

        # Add a pupil for getting the year group (and therefore slots)
        pupil = data_factories.Pupil(school=school, year_group=yg)

        # And a slot for getting the days
        slot = data_factories.TimetableSlot(school=school, relevant_year_groups=(yg,))

        lesson = data_factories.Lesson(
            school=school,
            pupils=(pupil,),
        )

        # Make a dummy slot at a different school
        data_factories.TimetableSlot(day_of_week=constants.Day.TUESDAY)

        # Execute test unit
        associated_days = lesson.get_usable_days_of_week()

        # Check outcome (and dummy not in answer)
        assert associated_days == [slot.day_of_week]

    def test_get_associated_timeslots_for_single_slot(self):
        """
        Test the correct list of days is returned for a year one lesson.
        """
        # Make a lesson with a slot
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)

        # Add a pupil for getting the year group (and therefore slots)
        pupil = data_factories.Pupil(school=school, year_group=yg)

        # And a slot for getting the days
        slot = data_factories.TimetableSlot(school=school, relevant_year_groups=(yg,))

        lesson = data_factories.Lesson(
            school=school,
            pupils=(pupil,),
        )

        # Make a dummy slot at a different school
        data_factories.TimetableSlot(day_of_week=constants.Day.TUESDAY)

        # Execute test unit
        associated_slots = lesson.get_associated_timeslots()

        # Check outcome
        assert associated_slots.count() == 1
        assert slot in associated_slots
        # We therefore have that the dummy wasn't associated
