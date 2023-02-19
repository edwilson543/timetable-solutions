"""Tests for forms relating to the Teacher model."""

import pytest

from interfaces.data_management import forms
from tests import data_factories


class TestTeacherUpdate:
    def test_teacher_attributes_set_as_initial_values(self):
        school = data_factories.School.build()
        teacher = data_factories.Teacher.build(school=school)

        form = forms.TeacherUpdate(school_id=school.school_access_key, teacher=teacher)

        assert form.school_id == school.school_access_key
        assert form.fields["firstname"].initial == teacher.firstname
        assert form.fields["surname"].initial == teacher.surname
        assert form.fields["title"].initial == teacher.title


@pytest.mark.django_db
class TestTeacherCreate:
    def test_form_valid_if_teacher_id_unique_for_school(self):
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

    def test_form_invalid_if_teacher_id_already_exists_for_school(self):
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

        assert (
            f"Teacher with id: {teacher.teacher_id} already exists!"
            in form.errors.as_text()
        )
