"""
Serializer classes for the basic school data models.
"""

# Third party imports
from rest_framework import serializers

# Local application imports
from data import constants, models
from domain.solver.queries import school as school_solver_queries
from interfaces.constants import UrlName


class YearGroup(serializers.Serializer):
    """
    Serialize year groups for use in template context.
    """

    year_group_id = serializers.IntegerField()
    year_group_name = serializers.CharField()

    # Relational data
    number_pupils = serializers.SerializerMethodField(method_name="_number_pupils")

    # Non-field data data
    update_url = serializers.SerializerMethodField(method_name="_get_update_url")

    def _number_pupils(self, obj: models.YearGroup) -> int:
        return obj.get_number_pupils()

    def _get_update_url(self, obj: models.YearGroup) -> str:
        """
        Get the url for this year groups's update / detail view page.
        """
        return UrlName.YEAR_GROUP_UPDATE.url(year_group_id=obj.year_group_id)


class Lesson(serializers.Serializer):
    """
    Serialize lessons for use in template context.
    """

    lesson_id = serializers.CharField()
    subject_name = serializers.CharField()
    year_group = serializers.SerializerMethodField(method_name="_year_group")
    teacher = serializers.SerializerMethodField(method_name="_teacher")
    classroom = serializers.SerializerMethodField(method_name="_classroom")
    total_required_slots = serializers.IntegerField()

    # Non-field data data
    update_url = serializers.SerializerMethodField(method_name="_get_update_url")

    def _year_group(self, obj: models.Lesson) -> str:
        return obj.get_associated_year_group().year_group_name

    def _teacher(self, obj: models.Lesson) -> str:
        if teacher := obj.teacher:
            return teacher.title + " " + teacher.surname
        return "N/A"

    def _classroom(self, obj: models.Lesson) -> str:
        if classroom := obj.classroom:
            return classroom.building + " " + str(classroom.room_number)
        return "N/A"

    def _get_update_url(self, obj: models.Lesson) -> str:
        """
        Get the url for this lesson's update / detail view page.
        """
        return UrlName.LESSON_UPDATE.url(lesson_id=obj.lesson_id)


class Teacher(serializers.Serializer):
    """
    Serialize teachers for use in template context.
    """

    teacher_id = serializers.IntegerField()
    firstname = serializers.CharField()
    surname = serializers.CharField()
    title = serializers.CharField()

    # Non-field data
    update_url = serializers.SerializerMethodField(method_name="_get_update_url")
    timetable_url = serializers.SerializerMethodField(method_name="_get_timetable_url")

    def _get_update_url(self, obj: models.Teacher) -> str:
        """
        Get the url for this teacher's update / detail view page.
        """
        return UrlName.TEACHER_UPDATE.url(teacher_id=obj.teacher_id)

    def _get_timetable_url(self, obj: models.Teacher) -> str:
        """
        Get the url for this teacher's timetable, if the school has timetable solutions.
        """
        if school_solver_queries.check_school_has_timetable_solutions(
            school=obj.school
        ):
            return UrlName.TEACHER_TIMETABLE.url(teacher_id=obj.teacher_id)
        return ""


class Classroom(serializers.Serializer):
    """
    Serialize classrooms for use in template context.
    """

    classroom_id = serializers.IntegerField()
    building = serializers.CharField()
    room_number = serializers.IntegerField()

    # Non-field data
    update_url = serializers.SerializerMethodField(method_name="_get_update_url")

    def _get_update_url(self, obj: models.Classroom) -> str:
        """
        Get the url for this classroom's update / detail view page.
        """
        return UrlName.CLASSROOM_UPDATE.url(classroom_id=obj.classroom_id)


class Pupil(serializers.Serializer):
    """
    Serialize pupils for use in template context.
    """

    pupil_id = serializers.IntegerField()
    firstname = serializers.CharField()
    surname = serializers.CharField()
    year_group = serializers.SerializerMethodField(method_name="_year_group_name")

    # Non-field data
    update_url = serializers.SerializerMethodField(method_name="_get_update_url")
    timetable_url = serializers.SerializerMethodField(method_name="_get_timetable_url")

    def _year_group_name(self, obj: models.Pupil) -> str:
        return obj.year_group.year_group_name

    def _get_update_url(self, obj: models.Pupil) -> str:
        """
        Get the url for this year group's update / detail view page.
        """
        return UrlName.PUPIL_UPDATE.url(pupil_id=obj.pupil_id)

    def _get_timetable_url(self, obj: models.Pupil) -> str:
        """
        Get the url for this pupils's timetable, if the school has timetable solutions.
        """
        if school_solver_queries.check_school_has_timetable_solutions(
            school=obj.school
        ):
            return UrlName.PUPIL_TIMETABLE.url(pupil_id=obj.pupil_id)
        return ""


class TimetableSlot(serializers.Serializer):
    """
    Serialize timetable slots for use in template context.
    """

    slot_id = serializers.IntegerField()
    day_of_week = serializers.SerializerMethodField(method_name="_day_of_week")
    starts_at = serializers.TimeField(format="%H:%M")
    ends_at = serializers.TimeField(format="%H:%M")

    # Relational data
    relevant_year_groups = YearGroup(many=True)

    # Non-field data
    update_url = serializers.SerializerMethodField(method_name="_get_update_url")

    def _day_of_week(self, obj: models.TimetableSlot) -> str:
        """
        Get the day of the week label from the value.
        """
        return constants.Day(obj.day_of_week).label

    def _get_update_url(self, obj: models.TimetableSlot) -> str:
        """
        Get the url for this slot's update / detail view page.
        """
        return UrlName.TIMETABLE_SLOT_UPDATE.url(slot_id=obj.slot_id)


class Break(serializers.Serializer):
    """
    Serialize breaks for use in template context.
    """

    break_id = serializers.CharField()
    break_name = serializers.CharField()
    day_of_week = serializers.SerializerMethodField(method_name="_day_of_week")
    starts_at = serializers.TimeField(format="%H:%M")
    ends_at = serializers.TimeField(format="%H:%M")

    # Relational data
    relevant_year_groups = YearGroup(many=True)
    teachers = Teacher(many=True)

    # Non-field data
    update_url = serializers.SerializerMethodField(method_name="_get_update_url")

    def _day_of_week(self, obj: models.Break) -> str:
        """
        Get the day of the week label from the value.
        """
        return constants.Day(obj.day_of_week).label

    def _get_update_url(self, obj: models.Break) -> str:
        """
        Get the url for this break's update / detail view page.
        """
        return UrlName.BREAK_UPDATE.url(break_id=obj.break_id)
