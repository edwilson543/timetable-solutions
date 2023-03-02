"""Unit tests for the methods on the TimetableSolverConstraints class"""


# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants as data_constants
from data import models
from domain import solver as slvr
from tests import data_factories, domain_factories


@pytest.mark.django_db
class TestSolverConstraints:
    # --------------------
    # Helpers
    # --------------------

    @staticmethod
    def get_constraint_maker(school: models.School) -> slvr.TimetableSolverConstraints:
        """Get an instance of the class we will be testing the methods of."""
        spec = domain_factories.SolutionSpecification()
        data = slvr.TimetableSolverInputs(
            school_id=school.school_access_key, solution_specification=spec
        )
        variables = slvr.TimetableSolverVariables(inputs=data)
        constraint_maker = slvr.TimetableSolverConstraints(
            inputs=data, variables=variables
        )
        return constraint_maker

    # --------------------
    # Tests
    # --------------------

    @pytest.mark.parametrize("n_lessons", [1, 41])
    def test_get_all_fulfillment_constraints(self, n_lessons):
        school = data_factories.School()

        for _ in range(0, n_lessons):
            # Get a n lessons that will need fulfilling, and one slot for each
            lesson = data_factories.Lesson.with_n_pupils(
                n_pupils=1,
                total_required_slots=1,
                total_required_double_periods=0,
                school=school,
            )
            data_factories.TimetableSlot(
                school=school,
                relevant_year_groups=(lesson.pupils.first().year_group,),
            )

        # Get the fulfillment constraints
        constraint_maker = self.get_constraint_maker(school=school)
        constraints = constraint_maker._get_all_fulfillment_constraints()

        # We should have one constraint: lesson_occurs_at_slot == 1
        for _ in range(0, n_lessons):
            constraint = next(constraints)[0]
            assert len(constraint) == 1
            assert constraint.constant == -1

        with pytest.raises(StopIteration):
            next(constraints)

    @pytest.mark.parametrize("n_pupils", [1, 17])
    def test_get_all_pupil_constraints_gives_a_constraint_per_pupil(
        self, n_pupils: int
    ):
        # Get a single lesson that will need fulfilling, and one slot
        lesson = data_factories.Lesson.with_n_pupils(
            n_pupils=n_pupils, total_required_slots=1, total_required_double_periods=0
        )
        data_factories.TimetableSlot(
            school=lesson.school,
            relevant_year_groups=(lesson.pupils.first().year_group,),
        )

        # Get the pupil constraints
        constraint_maker = self.get_constraint_maker(school=lesson.school)
        constraints = constraint_maker._get_all_pupil_constraints()

        # We should have one constraint per pupil, since there is one lesson and one slot
        for _ in range(0, n_pupils):
            constraint = next(constraints)[0]
            # Each constraint is of the form: busy_at_x <= 1
            assert len(constraint) == 1
            assert constraint.constant == -1

        with pytest.raises(StopIteration):
            next(constraints)

    @pytest.mark.parametrize("n_teachers", [1, 7])
    def test_get_all_teacher_constraints_gives_one_meaningful_per_teacher(
        self, n_teachers: int
    ):
        school = data_factories.School()

        # Get a lesson & one slot for each teacher to teach
        for _ in range(0, n_teachers):
            teacher = data_factories.Teacher(school=school)
            lesson = data_factories.Lesson.with_n_pupils(
                n_pupils=1,
                total_required_slots=1,
                total_required_double_periods=0,
                school=school,
                teacher=teacher,
            )
            data_factories.TimetableSlot(
                school=school,
                relevant_year_groups=(lesson.pupils.first().year_group,),
            )

        # Get the teacher constraints
        constraint_maker = self.get_constraint_maker(school=school)
        constraints = constraint_maker._get_all_teacher_constraints()

        # We should have one constraint per teacher, per slot.
        # Only one meaningful (non-zero) constraint per teacher however
        meaningful_constraints = 0
        zero_constraints = 0
        for constraint_tuple in constraints:
            constraint = constraint_tuple[0]
            if len(constraint) == 0:
                zero_constraints += 1
                continue

            # Each constraint is of the form: busy_at_x <= 1
            assert len(constraint) == 1
            assert constraint.constant == -1
            meaningful_constraints += 1

        # For each teacher we get one meaningful constraint
        # Which corresponds to them being busy at the slot they will teach in
        assert meaningful_constraints == n_teachers
        # And one dead constraint, corresponding to the slots they do not teach at
        assert zero_constraints == (n_teachers**2) - n_teachers

    def test_get_all_teacher_constraints_with_two_year_groups(self):
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)

        # Get two year groups and a lesson for each, both taught by the same teacher
        lesson_0 = data_factories.Lesson.with_n_pupils(
            n_pupils=1,
            total_required_slots=1,
            total_required_double_periods=0,
            school=school,
            teacher=teacher,
        )
        yg_0 = lesson_0.pupils.first().year_group
        slot_0 = data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg_0,),
            starts_at=dt.time(hour=10),
            ends_at=dt.time(hour=11),
        )

        lesson_1 = data_factories.Lesson.with_n_pupils(
            n_pupils=1,
            total_required_slots=1,
            total_required_double_periods=0,
            school=school,
            teacher=teacher,
        )
        yg_1 = lesson_1.pupils.first().year_group
        data_factories.TimetableSlot(  # Ensure this clashes with the other slot
            school=school,
            relevant_year_groups=(yg_1,),
            starts_at=dt.time(hour=9, minute=30),
            ends_at=dt.time(hour=10, minute=30),
            day_of_week=slot_0.day_of_week,
        )
        assert yg_0 != yg_1

        # Get the teacher constraints
        constraint_maker = self.get_constraint_maker(school=school)
        constraints = constraint_maker._get_all_teacher_constraints()

        # We should have a (duplicated) constraint that the teacher can't teach
        # at both of the factory slots, since they clash (the problem is infeasible)
        constraint_tuple = next(constraints)
        constraint = constraint_tuple[0]
        assert len(constraint) == 2
        assert constraint.constant == -1

    @pytest.mark.parametrize("n_classrooms", [1, 5])
    def test_get_all_classroom_constraints_gives_one_meaningful_per_classroom(
        self, n_classrooms
    ):
        school = data_factories.School()

        for _ in range(0, n_classrooms):
            # Get a lesson & one slot for each classroom to host
            classroom = data_factories.Classroom(school=school)
            lesson = data_factories.Lesson.with_n_pupils(
                n_pupils=1,
                total_required_slots=1,
                total_required_double_periods=0,
                school=school,
                classroom=classroom,
            )
            data_factories.TimetableSlot(
                school=school,
                relevant_year_groups=(lesson.pupils.first().year_group,),
            )

        # Get the classroom constraints
        constraint_maker = self.get_constraint_maker(school=school)
        constraints = constraint_maker._get_all_classroom_constraints()

        # We should have one constraint per teacher, per slot.
        # Only one meaningful (non-zero) constraint per teacher however
        meaningful_constraints = 0
        zero_constraints = 0
        for constraint_tuple in constraints:
            constraint = constraint_tuple[0]
            if len(constraint) == 0:
                zero_constraints += 1
                continue

            # Each constraint is of the form: busy_at_x <= 1
            assert len(constraint) == 1
            assert constraint.constant == -1
            meaningful_constraints += 1

        # For each classroom we get one meaningful constraint
        # Which corresponds to it being occupied at the slot it will have a lesson for
        assert meaningful_constraints == n_classrooms
        # And one dead constraint, corresponding to the slots they do not teach at
        assert zero_constraints == (n_classrooms**2) - n_classrooms

    def test_get_all_classroom_constraints_with_two_year_groups(self):
        school = data_factories.School()
        classroom = data_factories.Classroom(school=school)

        # Get two year groups and a lesson for each, both taught in the same classroom
        lesson_0 = data_factories.Lesson.with_n_pupils(
            n_pupils=1,
            total_required_slots=1,
            total_required_double_periods=0,
            school=school,
            classroom=classroom,
        )
        yg_0 = lesson_0.pupils.first().year_group
        slot_0 = data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg_0,),
            starts_at=dt.time(hour=10),
            ends_at=dt.time(hour=11),
        )

        lesson_1 = data_factories.Lesson.with_n_pupils(
            n_pupils=1,
            total_required_slots=1,
            total_required_double_periods=0,
            school=school,
            classroom=classroom,
        )
        yg_1 = lesson_1.pupils.first().year_group
        data_factories.TimetableSlot(  # Ensure this clashes with the other slot
            school=school,
            relevant_year_groups=(yg_1,),
            starts_at=dt.time(hour=9, minute=30),
            ends_at=dt.time(hour=10, minute=30),
            day_of_week=slot_0.day_of_week,
        )
        assert yg_0 != yg_1

        # Get the teacher constraints
        constraint_maker = self.get_constraint_maker(school=school)
        constraints = constraint_maker._get_all_classroom_constraints()

        # We should have a (duplicated) constraint that the classroom can't be used
        # at both of the factory slots, since they clash (the problem is infeasible)
        constraint = next(constraints)[0]
        assert len(constraint) == 2
        assert constraint.constant == -1

    @pytest.mark.parametrize("n_lessons", [1, 23])
    def test_get_all_double_period_fulfillment_constraints_one_per_lesson(
        self, n_lessons
    ):
        school = data_factories.School()

        for _ in range(0, n_lessons):
            # Get n lessons needing a double, and two consecutive slots for each
            lesson = data_factories.Lesson.with_n_pupils(
                n_pupils=1,
                total_required_slots=2,
                total_required_double_periods=1,
                school=school,
            )
            slot = data_factories.TimetableSlot(
                school=school,
                relevant_year_groups=(lesson.pupils.first().year_group,),
            )
            data_factories.TimetableSlot.get_next_consecutive_slot(slot)

        # Get the fulfillment constraints
        constraint_maker = self.get_constraint_maker(school=school)
        constraints = constraint_maker._get_all_double_period_fulfillment_constraints()

        # We should have one constraint: lesson_occurs_at_slot == 1
        for _ in range(0, n_lessons):
            constraint = next(constraints)[0]
            assert len(constraint) == 1
            assert constraint.constant == -1

        with pytest.raises(StopIteration):
            next(constraints)

    @pytest.mark.parametrize("n_lessons", [1, 11])
    def test_get_all_double_period_dependency_constraints_two_per_lesson(
        self, n_lessons
    ):
        school = data_factories.School()

        for _ in range(0, n_lessons):
            # Get n lessons needing a double, and two consecutive slots for each
            lesson = data_factories.Lesson.with_n_pupils(
                n_pupils=1,
                total_required_slots=2,
                total_required_double_periods=1,
                school=school,
            )
            slot = data_factories.TimetableSlot(
                school=school,
                relevant_year_groups=(lesson.pupils.first().year_group,),
            )
            data_factories.TimetableSlot.get_next_consecutive_slot(slot)

        # Get the dependency constraints
        constraint_maker = self.get_constraint_maker(school=school)
        constraints = constraint_maker._get_all_double_period_dependency_constraints()

        # Two constraints per lesson, since the double var depends on both single vars
        for _ in range(0, 2 * n_lessons):
            constraint = next(constraints)[0]
            # Each constraint is of the form: double_at_x_y <= double_at_x
            assert len(constraint) == 2
            assert constraint.constant == 0

        with pytest.raises(StopIteration):
            next(constraints)

    def test_get_all_no_two_doubles_in_a_day_constraint_one_per_day(self):
        # Get a lesson requiring a double
        lesson = data_factories.Lesson.with_n_pupils(
            n_pupils=1, total_required_slots=2, total_required_double_periods=1
        )
        # Offer 2 different options for the double (3 consecutive periods)
        slot_0 = data_factories.TimetableSlot(
            school=lesson.school,
            relevant_year_groups=(lesson.pupils.first().year_group,),
        )
        slot_1 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_0)
        data_factories.TimetableSlot.get_next_consecutive_slot(slot_1)

        # Make some noise from another year group,
        # Another pair of consecutive slots (which should just be ignored by the constraints)
        noise_0 = data_factories.TimetableSlot(school=lesson.school)
        data_factories.TimetableSlot.get_next_consecutive_slot(noise_0)

        # Get the dependency constraints
        constraint_maker = self.get_constraint_maker(school=lesson.school)
        constraints = constraint_maker._get_all_no_two_doubles_in_a_day_constraints()

        # Two constraints per lesson, since the double var depends on both single vars
        constraint = next(constraints)[0]
        # Constraint is: double_at_x_y + double_at_y_z <= 1
        assert len(constraint) == 2
        assert constraint.constant == -1

        with pytest.raises(StopIteration):
            next(constraints)

    def test_get_all_no_split_classes_within_day_constraints_constraints(self):
        # Get a lesson, requiring two distinct slots
        lesson = data_factories.Lesson.with_n_pupils(
            n_pupils=1,
        )

        # Split some classes within a single day
        data_factories.TimetableSlot(
            school=lesson.school,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
            day_of_week=data_constants.Day.MONDAY,
            relevant_year_groups=(lesson.pupils.first().year_group,),
        )
        data_factories.TimetableSlot(
            school=lesson.school,
            starts_at=dt.time(hour=15),
            ends_at=dt.time(hour=16),
            day_of_week=data_constants.Day.MONDAY,
            relevant_year_groups=(lesson.pupils.first().year_group,),
        )

        # Get the dependency constraints
        constraint_maker = self.get_constraint_maker(school=lesson.school)
        constraints = constraint_maker._get_all_no_split_classes_in_a_day_constraints()

        constraint = next(constraints)[0]
        # The constraint is: lesson at slot 1 + lesson at slot 2 <= 1
        assert len(constraint) == 2
        assert constraint.constant == -1

        with pytest.raises(StopIteration):
            next(constraints)
