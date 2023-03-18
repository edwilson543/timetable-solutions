"""
Serializer classes for the basic school data models.
"""

# Third party imports
from rest_framework import serializers

# Local application imports
from data import models
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

    def _year_group(self, obj: models.Lesson) -> str:
        return obj.get_associated_year_group().year_group_name

    def _teacher(self, obj: models.Lesson) -> dict[str, str]:
        if obj.teacher:
            return {
                "name": str(obj.teacher),
                "url": UrlName.TEACHER_UPDATE.url(teacher_id=obj.teacher.teacher_id),
            }
        else:
            return {}

    def _classroom(self, obj: models.Lesson) -> dict[str, str]:
        if obj.classroom:
            return {
                "name": str(obj.classroom),
                "url": UrlName.CLASSROOM_UPDATE.url(
                    classroom_id=obj.classroom.classroom_id
                ),
            }
        else:
            return {}


class Teacher(serializers.Serializer):
    """
    Serialize teachers for use in template context.
    """

    teacher_id = serializers.IntegerField()
    firstname = serializers.CharField()
    surname = serializers.CharField()
    title = serializers.CharField()

    # Relational data
    lessons = Lesson(many=True)

    # Non-field data
    update_url = serializers.SerializerMethodField(method_name="_get_update_url")

    def _get_update_url(self, obj: models.Teacher) -> str:
        """Get the url leading to this teacher's update / detail view page."""
        return UrlName.TEACHER_UPDATE.url(teacher_id=obj.teacher_id)


class Classroom(serializers.Serializer):
    """
    Serialize classrooms for use in template context.
    """

    classroom_id = serializers.IntegerField()
    building = serializers.CharField()
    room_number = serializers.IntegerField()

    # Relational data
    lessons = Lesson(many=True)

    # Non-field data
    update_url = serializers.SerializerMethodField(method_name="_get_update_url")

    def _get_update_url(self, obj: models.Classroom) -> str:
        """
        Get the url for this classroom's update / detail view page.
        """
        return UrlName.CLASSROOM_UPDATE.url(classroom_id=obj.classroom_id)


class Pupil(serializers.Serializer):
    """
    Serailize pupils for use in template context:
    """

    pupil_id = serializers.IntegerField()
    firstname = serializers.CharField()
    surname = serializers.CharField()

    # Relational data
    year_group = serializers.SerializerMethodField(method_name="_year_group_name")
    lessons = Lesson(many=True)

    # Non-field data
    update_url = serializers.SerializerMethodField(method_name="_get_update_url")

    def _year_group_name(self, obj: models.Pupil) -> str:
        return obj.year_group.year_group_name

    def _get_update_url(self, obj: models.Pupil) -> str:
        """
        Get the url for this pupil's update / detail view page.
        """
        return UrlName.PUPIL_UPDATE.url(pupil_id=obj.pupil_id)
