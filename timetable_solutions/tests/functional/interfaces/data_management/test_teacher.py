"""Tests for the teacher data management views."""

from django.contrib.auth import models as auth_models
from django import test
import pytest

from data import models
from interfaces.constants import UrlName
from tests import data_factories


@pytest.mark.django_db
class TestTeacherLanding:
    @pytest.mark.parametrize("has_existing_data", [True, False])
    def test_landing_page_loads(self, has_existing_data: bool):
        """
        Smoke test that a logged-in user can access the teacher landing page.

        The markup is slightly different depending on whether they have existing data,
        so test both cases.
        """
        # Create a user and log them in
        user = auth_models.User.objects.create_user(
            username="testing", password="unhashed"
        )
        profile = data_factories.Profile(user=user)
        if has_existing_data:
            data_factories.Teacher(school=profile.school)
        client = test.Client()
        client.login(username=user.username, password="unhashed")

        # Navigate to the teacher landing page
        url = UrlName.TEACHER_LANDING_PAGE.url()
        response = client.get(url)

        # Check the page loaded
        assert response.status_code == 200

    def test_anonymous_user_redirected(self):
        # Try to access landing page with an anonymous user
        client = test.Client()
        url = UrlName.TEACHER_LANDING_PAGE.url()
        response = client.get(url)

        # Check user is redirected to login page
        assert response.status_code == 302
        assert "users/accounts/login" in response.url


@pytest.mark.django_db
class TestTeacherSearchList:
    @staticmethod
    def get_authorised_client(school: models.School) -> test.Client:
        """Get a test client with a user authorised to perform the relevant actions."""
        user = auth_models.User.objects.create_user(
            username="testing", password="unhashed"
        )
        data_factories.Profile(user=user, school=school)
        client = test.Client()
        client.login(username=user.username, password="unhashed")
        return client

    def test_loads_all_teachers_for_school(self):
        # Create a user and log them in
        school = data_factories.School()
        client = self.get_authorised_client(school=school)

        data_factories.Teacher(school=school)
        data_factories.Teacher(school=school)

        # Create a teacher at some other school
        data_factories.Teacher()

        # Navigate to the teacher landing page
        url = UrlName.TEACHER_LIST.url()
        response = client.get(url)

        # Check the page loaded correctly
        assert response.status_code == 200

        form = response.context["form"]
        assert not form.errors

        teachers = response.context["object_list"]
        assert teachers.count() == 2

    def test_search_term_given_in_form_filters_teachers(self):
        # Create a user and log them in
        school = data_factories.School()
        client = self.get_authorised_client(school=school)

        teacher = data_factories.Teacher(school=school)
        # Create some other teacher to be excluded from the search
        data_factories.Teacher(school=school)

        # Navigate to the teacher landing page
        url = UrlName.TEACHER_LIST.url()

        form_data = {"search_term": teacher.firstname}
        response = client.post(url, data=form_data)

        # Check the page loaded
        assert response.status_code == 200

        form = response.context["form"]
        assert not form.errors

        teachers = response.context["object_list"]
        assert teachers.count() == 1
        assert teachers.get() == (
            teacher.teacher_id,
            teacher.firstname,
            teacher.surname,
        )

    def test_form_invalid_if_no_search_term(self):
        # Create a user and log them in
        school = data_factories.School()
        client = self.get_authorised_client(school=school)

        # Navigate to the teacher landing page
        url = UrlName.TEACHER_LIST.url()

        form_data = {}
        response = client.post(url, data=form_data)

        # Check the page loaded
        assert response.status_code == 200

        form = response.context["form"]
        assert form.errors
        assert "Please enter a search term!" in form.errors.as_text()
