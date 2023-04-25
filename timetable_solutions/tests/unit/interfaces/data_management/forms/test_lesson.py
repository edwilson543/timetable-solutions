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

        form = lesson_forms._LessonCreateUpdateBase(school_id=school.school_access_key)

        assert form.fields["teacher"].queryset.get() == teacher
        assert form.fields["classroom"].queryset.get() == classroom

    def test_cannot_have_incompatible_total_slots_and_total_doubles(self):
        school = data_factories.School()

        form = lesson_forms._LessonCreateUpdateBase(school_id=school.school_access_key)
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

        form = lesson_forms.LessonCreate(school_id=school.school_access_key)

        assert form.fields["year_group"].queryset.get() == year_group


@pytest.mark.django_db
class TestLessonUpdate:
    def test_clean_teacher_raises_if_teacher_would_have_clash(self):
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)

        # Make a lesson the teacher is busy with
        slot = data_factories.TimetableSlot(school=school)
        data_factories.Lesson(
            school=school, user_defined_time_slots=(slot,), teacher=teacher
        )

        # Make a lesson to try adding the teacher to
        lesson = data_factories.Lesson(school=school, user_defined_time_slots=(slot,))

        form = lesson_forms.LessonUpdate(
            school_id=school.school_access_key, lesson=lesson
        )
        form.cleaned_data = {"teacher": teacher}

        with pytest.raises(django_exceptions.ValidationError) as exc:
            form.clean_teacher()

        assert "already have a lesson that clashes" in str(exc.value)

    def test_clean_classroom_raises_if_classroom_would_have_clash(self):
        school = data_factories.School()
        classroom = data_factories.Classroom(school=school)

        # Make a lesson the classroom is occupied with
        slot = data_factories.TimetableSlot(school=school)
        data_factories.Lesson(
            school=school, user_defined_time_slots=(slot,), classroom=classroom
        )

        # Make a lesson to try adding the teacher to
        lesson = data_factories.Lesson(school=school, user_defined_time_slots=(slot,))

        form = lesson_forms.LessonUpdate(
            school_id=school.school_access_key, lesson=lesson
        )
        form.cleaned_data = {"classroom": classroom}

        with pytest.raises(django_exceptions.ValidationError) as exc:
            form.clean_classroom()

        assert "already has a lesson that clashes" in str(exc.value)


@pytest.mark.django_db
class TestLessonAddPupil:
    def test_initialisation_sets_correct_pupil_options(self):
        school = data_factories.School()

        # Make a lesson with a pupil we don't expect in the add pupil options
        lesson = data_factories.Lesson.with_n_pupils(n_pupils=1, school=school)

        # This is the only pupil we expect in the add pupil options
        other_pupil = data_factories.Pupil(school=school)

        # Make a pupil at some other school
        other_school_pupil = data_factories.Pupil()
        assert other_school_pupil.school != school

        form = lesson_forms.LessonAddPupil(
            school_id=school.school_access_key, lesson=lesson
        )

        assert form.fields["pupil"].queryset.get() == other_pupil

    def test_clean_pupil_raises_if_pupil_would_have_clash(self):
        school = data_factories.School()

        # Make a lesson the pupil is bust with
        slot = data_factories.TimetableSlot(school=school)
        pupil = data_factories.Pupil(school=school)
        data_factories.Lesson(
            school=school, pupils=(pupil,), user_defined_time_slots=(slot,)
        )

        # Make another lesson with the same pre-defined slots to try adding the pupil to
        lesson = data_factories.Lesson(school=school, user_defined_time_slots=(slot,))

        form = lesson_forms.LessonAddPupil(
            school_id=school.school_access_key, lesson=lesson
        )
        form.cleaned_data = {"pupil": pupil}

        with pytest.raises(django_exceptions.ValidationError) as exc:
            form.clean_pupil()

        assert "already have a lesson that clashes" in str(exc.value)


@pytest.mark.django_db
class TestLessonAddUserDefinedTimetableSlot:
    def test_initialisation_sets_correct_slot_options(self):
        school = data_factories.School()

        # Make a lesson with a slot we don't expect in the add pupil options
        already_in_use_slots = data_factories.TimetableSlot(school=school)
        lesson = data_factories.Lesson(
            school=school, user_defined_time_slots=(already_in_use_slots,)
        )

        # This is the only slot we expect in the add pupil options
        slot = data_factories.TimetableSlot(school=school)

        # Make a slot at some other school
        other_school_slot = data_factories.TimetableSlot()
        assert other_school_slot.school != school

        form = lesson_forms.LessonAddUserDefinedTimetableSlot(
            school_id=school.school_access_key, lesson=lesson
        )

        assert form.fields["slot"].queryset.get() == slot

    def test_slot_field_disabled_if_already_has_required_number_of_slots(self):
        school = data_factories.School()

        slot = data_factories.TimetableSlot(school=school)
        lesson = data_factories.Lesson(
            school=school, user_defined_time_slots=(slot,)
        )

        form = lesson_forms.LessonAddUserDefinedTimetableSlot(
            school_id=school.school_access_key, lesson=lesson
        )

        assert form.fields["slot"].disabled

    def test_form_not_valid_if_teacher_would_have_clash(self):
        school = data_factories.School()

        # Make a teacher busy at some slot
        already_in_use_slot = data_factories.TimetableSlot(school=school)
        teacher = data_factories.Teacher(school=school)
        data_factories.Lesson(
            school=school,
            user_defined_time_slots=(already_in_use_slot,),
            teacher=teacher,
        )

        # Make another slot at the same time
        slot = data_factories.TimetableSlot(
            school=school,
            day_of_week=already_in_use_slot.day_of_week,
            starts_at=already_in_use_slot.starts_at,
            ends_at=already_in_use_slot.ends_at,
        )

        # Make a lesson with the same teacher to try adding the slot to
        lesson = data_factories.Lesson(school=school, teacher=teacher)

        form = lesson_forms.LessonAddUserDefinedTimetableSlot(
            school_id=school.school_access_key, lesson=lesson
        )
        form.cleaned_data = {"slot": slot}

        with pytest.raises(django_exceptions.ValidationError) as exc:
            form.clean_slot()

        assert "the lesson's teacher is already busy" in str(exc.value)

    def test_form_not_valid_if_classroom_would_have_clash(self):
        school = data_factories.School()

        # Make a classroom busy at some slot
        already_in_use_slot = data_factories.TimetableSlot(school=school)
        classroom = data_factories.Classroom(school=school)
        data_factories.Lesson(
            school=school,
            user_defined_time_slots=(already_in_use_slot,),
            classroom=classroom,
        )

        # Make another slot at the same time
        slot = data_factories.TimetableSlot(
            school=school,
            day_of_week=already_in_use_slot.day_of_week,
            starts_at=already_in_use_slot.starts_at,
            ends_at=already_in_use_slot.ends_at,
        )

        # Make a lesson with the same classroom to try adding the slot to
        lesson = data_factories.Lesson(school=school, classroom=classroom)

        form = lesson_forms.LessonAddUserDefinedTimetableSlot(
            school_id=school.school_access_key, lesson=lesson
        )
        form.cleaned_data = {"slot": slot}

        with pytest.raises(django_exceptions.ValidationError) as exc:
            form.clean_slot()

        assert "the lesson's classroom is already busy" in str(exc.value)

    def test_form_not_valid_if_a_pupil_would_have_clash(self):
        school = data_factories.School()

        # Make a pupil busy at some slot
        already_in_use_slot = data_factories.TimetableSlot(school=school)
        pupil = data_factories.Pupil(school=school)
        data_factories.Lesson(
            school=school,
            user_defined_time_slots=(already_in_use_slot,),
            pupils=(pupil,),
        )

        # Make another slot at the same time
        slot = data_factories.TimetableSlot(
            school=school,
            day_of_week=already_in_use_slot.day_of_week,
            starts_at=already_in_use_slot.starts_at,
            ends_at=already_in_use_slot.ends_at,
        )

        # Make a lesson with the same teacher to try adding the slot to
        lesson = data_factories.Lesson(school=school, pupils=(pupil,))

        form = lesson_forms.LessonAddUserDefinedTimetableSlot(
            school_id=school.school_access_key, lesson=lesson
        )
        form.cleaned_data = {"slot": slot}

        with pytest.raises(django_exceptions.ValidationError) as exc:
            form.clean_slot()

        assert "one of the pupils in this lesson is already busy" in str(exc.value)
