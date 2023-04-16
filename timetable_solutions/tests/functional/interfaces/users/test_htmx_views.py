"""
Module containing unit tests for HTMX request handlers.
"""


# Django imports
from django import test, urls

# Local application imports
from interfaces.constants import UrlName
from interfaces.users import htmx_views


class TestHTMXViewsRegister(test.TestCase):
    """
    Tests for the view functions handling http requests made using HTMX on the registration page.
    """

    fixtures = ["user_school_profile.json"]

    def run_boilerplate_test(self, username: str, expected_status: str) -> None:
        """
        Equivalent to using pytest parameterize but with a fixture installed
        """
        # Set test parameters
        url = urls.reverse(UrlName.USERNAME_FIELD_REGISTRATION.value)
        form_data = {"username": username}

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check outcome
        status = response.context["USERNAME_VALID"]
        assert status == expected_status

    def test_username_taken_gets_invalid_status(self):
        """
        Tests that posting a username that is already taken returns an invalid status in the context.
        """
        self.run_boilerplate_test(
            username="dummy_teacher", expected_status=htmx_views.FieldStatus.INVALID
        )

    def test_username_available_gets_valid_status(self):
        """
        Tests that posting a username that is already taken returns an invalid status in the context.
        """
        self.run_boilerplate_test(
            username="available", expected_status=htmx_views.FieldStatus.VALID
        )

    def test_username_containing_invalid_characters_gets_invalid_status(self):
        """
        Tests that posting a username that is already taken returns an invalid status in the context.
        """
        self.run_boilerplate_test(
            username="!!!!!", expected_status=htmx_views.FieldStatus.INVALID
        )
