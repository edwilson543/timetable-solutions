"""
Tests for the related lessons table on the pupil update view.
"""

# Standard library imports
from collections import OrderedDict
from unittest import mock

# Local application imports
from interfaces.constants import UrlName
from interfaces.data_management import views
from tests import data_factories
from tests.functional import client


class TestPupilLessonsPartial(client.TestClient):
    def test_loads_table_with_correct_context(self):
        school = data_factories.School()
        self.authorise_client_for_school(school=school)

        # Make a pupil with two lessons
        pupil = data_factories.Pupil(school=school)
        lesson_a = data_factories.Lesson(
            school=school, lesson_id="aaa", pupils=(pupil,)
        )
        lesson_b = data_factories.Lesson(
            school=school, lesson_id="bbb", pupils=(pupil,)
        )

        # Get the partial
        url = UrlName.PUPIL_LESSONS_PARTIAL.url(pupil_id=pupil.pupil_id)
        response = self.client.get(url, headers={"HX-Request": "true"})

        # Ensure response ok and the correct context was loaded
        assert response.status_code == 200
        assert response.context["page_obj"].object_list == [
            OrderedDict(
                [
                    ("lesson_id", lesson_a.lesson_id),
                    ("subject_name", lesson_a.subject_name),
                    ("year_group", pupil.year_group.year_group_name),
                    ("teacher", f"{lesson_a.teacher.title} {lesson_a.teacher.surname}"),
                    (
                        "classroom",
                        f"{lesson_a.classroom.building} {lesson_a.classroom.room_number}",
                    ),
                    ("total_required_slots", lesson_a.total_required_slots),
                ]
            ),
            OrderedDict(
                [
                    ("lesson_id", lesson_b.lesson_id),
                    ("subject_name", lesson_b.subject_name),
                    ("year_group", pupil.year_group.year_group_name),
                    ("teacher", f"{lesson_b.teacher.title} {lesson_b.teacher.surname}"),
                    (
                        "classroom",
                        f"{lesson_b.classroom.building} {lesson_b.classroom.room_number}",
                    ),
                    ("total_required_slots", lesson_b.total_required_slots),
                ]
            ),
        ]

    @mock.patch.object(views.PupilLessonsPartial, "paginate_by", return_value=1)
    def test_loads_second_page_of_table_when_data_paginated(
        self, mock_paginate_by: mock.Mock
    ):
        school = data_factories.School()
        self.authorise_client_for_school(school=school)

        # Make a pupil with two lessons
        pupil = data_factories.Pupil(school=school)
        data_factories.Lesson(school=school, lesson_id="aaa", pupils=(pupil,))
        lesson_b = data_factories.Lesson(
            school=school, lesson_id="bbb", pupils=(pupil,)
        )

        # Get the partial
        url = UrlName.PUPIL_LESSONS_PARTIAL.url(pupil_id=pupil.pupil_id)
        url += "?page=2"
        response = self.client.get(url, headers={"HX-Request": "true"})

        # Ensure response ok and the correct context was loaded
        assert response.status_code == 200
        assert response.context["page_obj"].object_list == [
            OrderedDict(
                [
                    ("lesson_id", lesson_b.lesson_id),
                    ("subject_name", lesson_b.subject_name),
                    ("year_group", pupil.year_group.year_group_name),
                    ("teacher", f"{lesson_b.teacher.title} {lesson_b.teacher.surname}"),
                    (
                        "classroom",
                        f"{lesson_b.classroom.building} {lesson_b.classroom.room_number}",
                    ),
                    ("total_required_slots", lesson_b.total_required_slots),
                ]
            )
        ]
