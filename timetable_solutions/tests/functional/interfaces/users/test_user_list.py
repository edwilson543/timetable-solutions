"""
Tests for the page listing a school's users.
"""

# Local application imports
from data import constants
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestUserProfileList(TestClient):
    def test_loads_all_users_for_school(self):
        # Create a school and authorise the test client for this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some users for the school (which will be alphabetically sorted by firstname)
        user_a = data_factories.User(username="alex")
        data_factories.Profile(
            user=user_a, school=school, role=constants.UserRole.SCHOOL_ADMIN
        )
        user_b = data_factories.User(username="ben")
        data_factories.Profile(
            user=user_b, school=school, role=constants.UserRole.TEACHER
        )

        # Create a year group at some other school
        data_factories.Profile()

        # Navigate to the users list view
        url = UrlName.USER_LIST.url()
        response = self.client.get(url)

        # Check response ok and has the correct context
        assert response.status_code == 200

        serialized_users = response.context["page_obj"].object_list
        serialized_user_profile_a = serialized_users[0]
        serialized_user_profile_b = serialized_users[1]

        assert serialized_user_profile_a["username"] == "alex"
        assert (
            serialized_user_profile_a["role"] == constants.UserRole.SCHOOL_ADMIN.label
        )

        assert serialized_user_profile_b["username"] == "ben"
        assert serialized_user_profile_b["role"] == constants.UserRole.TEACHER.label
