"""Operations on the Break model affecting db state."""

# Django imports
from django.db import IntegrityError

# Local application imports
from data import models
from domain.data_management import base_exceptions


class UnableToCreateLesson(base_exceptions.UnableToCreateModelInstance):
    pass


def create_new_lesson(
    *,
    school_id: int,
    lesson_id: str,
    subject_name: str,
    total_required_slots: int,
    total_required_double_periods: int,
    teacher_id: int | None = None,
    classroom_id: int | None = None,
    pupils: models.PupilQuerySet | None = None,
    user_defined_time_slots: models.TimetableSlotQuerySet | None = None,
) -> models.Lesson:
    """
    Create a new lesson in the db.

    :raises CouldNotCreateLesson: if the parameters could not be used to create a lesson.
    """
    if teacher_id:
        try:
            teacher = models.Teacher.objects.get(
                school_id=school_id, teacher_id=teacher_id
            )
        except models.Teacher.DoesNotExist as exc:
            raise UnableToCreateLesson(
                human_error_message=f"Teacher with id {teacher_id} does not exist!"
            ) from exc
    else:
        teacher = None

    if classroom_id:
        try:
            classroom = models.Classroom.objects.get(
                school_id=school_id, classroom_id=classroom_id
            )
        except models.Classroom.DoesNotExist as exc:
            raise UnableToCreateLesson(
                human_error_message=f"Classroom with id {classroom_id} does not exist!"
            ) from exc
    else:
        classroom = None

    try:
        return models.Lesson.create_new(
            school_id=school_id,
            lesson_id=lesson_id,
            subject_name=subject_name,
            total_required_slots=total_required_slots,
            total_required_double_periods=total_required_double_periods,
            teacher=teacher,
            classroom=classroom,
            pupils=pupils,
            user_defined_time_slots=user_defined_time_slots,
        )
    except IntegrityError as exc:
        raise UnableToCreateLesson(
            human_error_message="Could not create lesson with the given data."
        ) from exc
