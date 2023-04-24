# Third party imports
import pytest

# Django imports
from django.core import exceptions as django_exceptions

# Local application imports
from interfaces.data_management.forms import lesson as lesson_forms
from tests import data_factories


@pytest.mark.django_db
class TestLessonCreateUpdateBase:
    def test_initialisation_sets_teacher_and_classroom_options(self):
        # Make a teacher and classroom at the same school
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)
        classroom = data_factories.Classroom(school=school)

        # Make a classroom and teacher at some other school
        other_teacher = data_factories.Teacher()
        assert other_teacher.school != school
        other_classroom = data_factories.Classroom()
        assert other_classroom.school != school

        form = lesson_forms._LessonCreateUpdateBase(school=school)

        assert form.fields["teacher"].queryset.get() == teacher
        assert form.fields["classroom"].queryset.get() == classroom

    def test_cannot_have_incompatible_total_slots_and_total_doubles(self):
        school = data_factories.School()

        form = lesson_forms._LessonCreateUpdateBase(school=school)
        form.cleaned_data = {
            "total_required_slots": 1,
            "total_required_double_periods": 2,
        }

        with pytest.raises(django_exceptions.ValidationError) as exc:
            form.clean()

        assert "must be at most half the total number of required slots" in str(
            exc.value
        )


@pytest.mark.django_db
class TestLessonCreate:
    def test_initialisation_sets_year_group_options(self):
        school = data_factories.School()
        year_group = data_factories.YearGroup(school=school)

        # Make a classroom and teacher at some other school
        other_yg = data_factories.YearGroup()
        assert other_yg.school != school

        form = lesson_forms.LessonCreate(school=school)

        assert form.fields["year_group"].queryset.get() == year_group


@pytest.mark.django_db
class TestLessonUpdate:
    def test_raises_if_teacher_would_have_clash(self):
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)

        # Make a lesson the teacher is busy with
        slot = data_factories.TimetableSlot(school=school)
        data_factories.Lesson(
            school=school, user_defined_time_slots=(slot,), teacher=teacher
        )

        # Make a lesson to try adding the teacher to
        lesson = data_factories.Lesson(school=school, user_defined_time_slots=(slot,))

        form = lesson_forms.LessonUpdate(school=school, lesson=lesson)
        form.cleaned_data = {"teacher": teacher}

        with pytest.raises(django_exceptions.ValidationError) as exc:
            form.clean_teacher()

        assert "already have a lesson that clashes" in str(exc.value)

    def test_raises_if_classroom_would_have_clash(self):
        school = data_factories.School()
        classroom = data_factories.Classroom(school=school)

        # Make a lesson the classroom is occupied with
        slot = data_factories.TimetableSlot(school=school)
        data_factories.Lesson(
            school=school, user_defined_time_slots=(slot,), classroom=classroom
        )

        # Make a lesson to try adding the teacher to
        lesson = data_factories.Lesson(school=school, user_defined_time_slots=(slot,))

        form = lesson_forms.LessonUpdate(school=school, lesson=lesson)
        form.cleaned_data = {"classroom": classroom}

        with pytest.raises(django_exceptions.ValidationError) as exc:
            form.clean_classroom()

        assert "already has a lesson that clashes" in str(exc.value)
