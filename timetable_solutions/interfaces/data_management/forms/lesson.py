"""
Forms relating to the Lesson model.
"""

# Standard library imports
from typing import Any

# Django imports
from django import forms as django_forms

# Local application imports
from data import models
from domain.solver.queries import classroom as classroom_solver_queries
from domain.solver.queries import pupil as pupil_solver_queries
from domain.solver.queries import teacher as teacher_solver_queries


class LessonSearch(django_forms.Form):
    """
    Search form for the lesson model.
    """

    search_term = django_forms.CharField(
        required=True, label="Search for a lesson by subject name or id"
    )


class _LessonCreateUpdateBase(django_forms.Form):
    """
    Base form for creating and updating lessons.
    """

    # Actually quite simple given no slots
    # Validate total required versus total doubles

    subject_name = django_forms.CharField(label="Subject name", max_length=20)
    teacher = django_forms.ModelChoiceField(
        label="Teacher", required=False, queryset=models.Teacher.objects.none()
    )
    classroom = django_forms.ModelChoiceField(
        label="Classroom", required=False, queryset=models.Classroom.objects.none()
    )
    total_required_slots = django_forms.IntegerField(
        label="Total required slots per week", min_value=1
    )
    total_required_double_periods = django_forms.IntegerField(
        label="Total required double periods per week", min_value=0
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Set the teacher and classroom options.
        """
        self.school_id = kwargs.pop("school_id")
        super().__init__(*args, **kwargs)

        teachers = models.Teacher.objects.filter(school_id=self.school_id).order_by(
            "firstname"
        )
        self.fields["teacher"].queryset = teachers

        classrooms = models.Classroom.objects.filter(school_id=self.school_id).order_by(
            "building", "room_number"
        )
        self.fields["classroom"].queryset = classrooms

    def clean(self) -> dict[str, Any]:
        """
        Ensure total required slots and total required double periods are compatible
        """
        total_required_slots = self.cleaned_data.get("total_required_slots", 1)
        total_required_double_periods = self.cleaned_data.get(
            "total_required_double_periods", 0
        )
        if total_required_double_periods * 2 > total_required_slots:
            raise django_forms.ValidationError(
                "Total required double periods must be at most half the total number of required slots"
            )
        return self.cleaned_data


class LessonCreate(_LessonCreateUpdateBase):
    lesson_id = django_forms.CharField(label="Lesson ID", max_length=20)
    year_group = django_forms.ModelChoiceField(
        label="Year group", empty_label="", queryset=models.YearGroup.objects.none()
    )

    field_order = [
        "lesson_id",
        "subject_name",
        "teacher",
        "classroom",
        "year_group",
        "total_required_slots",
        "total_required_double_periods",
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Set the year group options.
        """
        super().__init__(*args, **kwargs)
        year_groups = models.YearGroup.objects.filter(
            school_id=self.school_id
        ).order_by("year_group_name")
        self.fields["year_group"].queryset = year_groups


class LessonUpdate(_LessonCreateUpdateBase):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.lesson = kwargs.pop("lesson")
        super().__init__(*args, **kwargs)

    def clean_teacher(self) -> models.Teacher | None:
        """
        Ensure the updated teacher would have no clashes if added to this lesson.
        """
        if (
            not (teacher := self.cleaned_data.get("teacher"))
            or teacher == self.lesson.teacher  # Teacher is unchanged
        ):
            return None

        # Check the updated teacher is not busy at any of the time slots
        clashes = []
        for slot in self.lesson.user_defined_time_slots.all():
            if clash := teacher_solver_queries.check_if_teacher_busy_at_time(
                teacher=teacher,
                starts_at=slot.starts_at,
                ends_at=slot.ends_at,
                day_of_week=slot.day_of_week,
            ):
                clashes.append(clash)

        if clashes:
            raise django_forms.ValidationError(
                f"Cannot update teacher to {teacher}, since they already have a lesson that clashes "
                "with at least one of your pre-defined time slots"
            )

        return teacher

    def clean_classroom(self) -> models.Teacher | None:
        """
        Ensure the updated classroom would have no clashes if added to this lesson.
        """
        if (
            not (classroom := self.cleaned_data.get("classroom"))
            or classroom == self.lesson.classroom  # Classroom is unchanged
        ):
            return None

        # Check the updated teacher is not busy at any of the time slots
        clashes = []
        for slot in self.lesson.user_defined_time_slots.all():
            if clash := classroom_solver_queries.check_if_classroom_occupied_at_time(
                classroom=classroom,
                starts_at=slot.starts_at,
                ends_at=slot.ends_at,
                day_of_week=slot.day_of_week,
            ):
                clashes.append(clash)

        if clashes:
            raise django_forms.ValidationError(
                f"Cannot update classroom to {classroom}, since it already has a lesson that clashes "
                "with at least one of your pre-defined time slots"
            )

        return classroom


class LessonAddPupil(django_forms.Form):
    pupil = django_forms.ModelChoiceField(
        label="Add a pupil to this lesson",
        empty_label="",
        queryset=models.Pupil.objects.none(),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Set the pupils that can be added.
        """
        school_id = kwargs.pop("school_id")
        self.lesson = kwargs.pop("lesson")
        super().__init__(*args, **kwargs)

        exclude_pks = self.lesson.pupils.values_list("pk", flat=True)
        pupils = (
            models.Pupil.objects.filter(school_id=school_id)
            .exclude(pk__in=exclude_pks)
            .order_by("firstname")
        )
        if pupils:
            self.fields["pupil"].queryset = pupils
        elif (
            self.lesson.user_defined_time_slots.count()
            == self.lesson.total_required_slots
        ):
            self.fields["slot"].disabled = True
            self.fields["slot"] = "This lesson already has its required number of slots"
        else:
            self.fields["pupil"].disabled = True
            self.fields["pupil"].help_text = "All pupils have been added to this lesson"

    def clean_pupil(self) -> models.Pupil:
        pupil = self.cleaned_data["pupil"]
        clashes = []
        for slot in self.lesson.user_defined_time_slots.all():
            if clash := pupil_solver_queries.check_if_pupil_busy_at_time(
                pupil=pupil,
                starts_at=slot.starts_at,
                ends_at=slot.ends_at,
                day_of_week=slot.day_of_week,
            ):
                clashes.append(clash)

        if clashes:
            raise django_forms.ValidationError(
                f"Cannot add {pupil} to lesson, since they already have a lesson that clashes "
                "with at least one of your pre-defined time slots"
            )

        return pupil


class LessonAddUserDefinedTimetableSlot(django_forms.Form):
    slot = django_forms.ModelChoiceField(
        label="Pre-define a slot when this lesson must take place",
        empty_label="",
        queryset=models.TimetableSlot.objects.none(),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Set the slots that can be added.
        """
        school_id = kwargs.pop("school_id")
        self.lesson = kwargs.pop("lesson")
        super().__init__(*args, **kwargs)

        # if self.lesson.user_defined_time_slots.count() == self.lesson.total_required_slots:
        #     self.fields["slot"].disabled = True
        #     self.fields["slot"] = "This lesson already has its required number of slots"
        #     return None

        exclude_pks = self.lesson.user_defined_time_slots.values_list("pk", flat=True)
        slots = (
            models.TimetableSlot.objects.filter(school_id=school_id)
            .exclude(pk__in=exclude_pks)
            .order_by("day_of_week", "starts_at")
        )
        if slots:
            self.fields["slot"].queryset = slots
        else:
            self.fields["slot"].disabled = True

    def clean_slot(self) -> models.TimetableSlot:
        """
        Check no pupil, teacher or pupil would be given a clash if added to the lesson.
        """
        slot = self.cleaned_data["slot"]

        # Check the lesson's teacher would be given a clash
        if teacher_solver_queries.check_if_teacher_busy_at_time(
            teacher=self.lesson.teacher,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
        ):
            raise django_forms.ValidationError(
                f"Cannot add {slot}, since the lesson's teacher "
                "is already busy at this time"
            )

        if classroom_solver_queries.check_if_classroom_occupied_at_time(
            classroom=self.lesson.classroom,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
        ):
            raise django_forms.ValidationError(
                f"Cannot add {slot}, since the lesson's classroom "
                "is already busy at this time"
            )

        # Check none of the lesson's pupils would be given a clash
        pupil_clashes = []
        for pupil in self.lesson.pupils.all():
            if clash := pupil_solver_queries.check_if_pupil_busy_at_time(
                pupil=pupil,
                starts_at=slot.starts_at,
                ends_at=slot.ends_at,
                day_of_week=slot.day_of_week,
            ):
                pupil_clashes.append(clash)
        if pupil_clashes:
            raise django_forms.ValidationError(
                f"Cannot add {slot}, since at least one of the pupils in this "
                "lesson is already busy at this time"
            )

        return slot
