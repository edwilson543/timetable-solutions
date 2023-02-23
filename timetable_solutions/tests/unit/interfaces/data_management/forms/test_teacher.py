"""Tests for forms relating to the Teacher model."""

from unittest import mock

import pytest

from interfaces.data_management import forms
from tests import data_factories


@pytest.mark.django_db
class TestTeacherCreate:
    @mock.patch(
        "interfaces.data_management.forms.teacher.queries.get_next_teacher_id_for_school",
    )
    @mock.patch(
        "interfaces.data_management.forms.teacher.queries.get_teacher_for_school",
        return_value=False,
    )
    def test_form_valid_if_teacher_id_unique_for_school(
        self, mock_get_teacher: mock.Mock(), mock_get_next_teacher: mock.Mock()
    ):
        school = data_factories.School()

        form = forms.TeacherCreate(
            school_id=school.school_access_key,
            data={
                "teacher_id": 1,
                "firstname": "test-firstname",
                "surname": "test-surname",
                "title": "test-title",
            },
        )

        assert form.is_valid()

        assert form.cleaned_data["firstname"] == "test-firstname"
        assert form.cleaned_data["surname"] == "test-surname"
        assert form.cleaned_data["title"] == "test-title"

    @mock.patch(
        "interfaces.data_management.forms.teacher.queries.get_next_teacher_id_for_school",
        return_value=123456,
    )
    @mock.patch(
        "interfaces.data_management.forms.teacher.queries.get_teacher_for_school",
        return_value=True,
    )
    def test_form_invalid_if_teacher_id_already_exists_for_school(
        self, mock_get_teacher: mock.Mock(), mock_get_next_teacher: mock.Mock()
    ):
        teacher = data_factories.Teacher()

        form = forms.TeacherCreate(
            school_id=teacher.school.school_access_key,
            data={
                "teacher_id": teacher.teacher_id,
                "firstname": "test-firstname",
                "surname": "test-surname",
                "title": "test-title",
            },
        )

        assert not form.is_valid()
        errors = form.errors.as_text()

        assert f"Teacher with id: {teacher.teacher_id} already exists!" in errors
        assert f"The next available id is: 123456" in errors

    @mock.patch(
        "interfaces.data_management.forms.teacher.queries.get_next_teacher_id_for_school",
        return_value=123456,
    )
    def test_form_init_sets_next_teacher_id(self, mock_get_next_teacher: mock.Mock()):
        form = forms.TeacherCreate(school_id=1)

        assert form.school_id == 1
        # The test class mocks the query for the next teacher_id to be 10
        assert form.base_fields["teacher_id"].initial == 123456
