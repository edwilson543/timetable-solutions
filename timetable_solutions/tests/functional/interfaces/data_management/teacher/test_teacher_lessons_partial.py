""""
Tests for the related lessons table on the teacher update view.
"""
# Standard library imports
from unittest import mock

# Local application imports
from interfaces.constants import UrlName
from interfaces.data_management import views
from tests import data_factories
from tests.functional import client
from tests.helpers import serializers as serializers_helpers


class TestTeacherLessonsPartial(client.TestClient):
    def test_loads_table_with_correct_context(self):
        school = data_factories.School()
        self.authorise_client_for_school(school=school)

        # Make a teacher with two lessons
        teacher = data_factories.Teacher(school=school)
        lesson_a = data_factories.Lesson.with_n_pupils(
            school=school, teacher=teacher, lesson_id="aaa"
        )
        lesson_b = data_factories.Lesson.with_n_pupils(
            school=school, teacher=teacher, lesson_id="bbb"
        )

        # Get the partial
        url = UrlName.TEACHER_LESSONS_PARTIAL.url(teacher_id=teacher.teacher_id)
        response = self.client.get(url, headers={"HX-Request": "true"})

        # Ensure response ok and the correct context was loaded
        assert response.status_code == 200
        assert response.context["page_obj"].object_list == [
            serializers_helpers.expected_lesson(lesson_a),
            serializers_helpers.expected_lesson(lesson_b),
        ]

    @mock.patch.object(views.TeacherLessonsPartial, "paginate_by", return_value=1)
    def test_loads_second_page_of_table_when_data_paginated(
        self, mock_paginate_by: mock.Mock
    ):
        school = data_factories.School()
        self.authorise_client_for_school(school=school)

        # Make a teacher with two lessons
        teacher = data_factories.Teacher(school=school)
        data_factories.Lesson.with_n_pupils(
            school=school, teacher=teacher, lesson_id="aaa"
        )
        lesson_b = data_factories.Lesson.with_n_pupils(
            school=school, teacher=teacher, lesson_id="bbb"
        )

        # Get the partial
        url = UrlName.TEACHER_LESSONS_PARTIAL.url(teacher_id=teacher.teacher_id)
        url += "?page=2"
        response = self.client.get(url, headers={"HX-Request": "true"})

        # Ensure response ok and the correct context was loaded
        assert response.status_code == 200
        assert response.context["page_obj"].object_list == [
            serializers_helpers.expected_lesson(lesson_b),
        ]
