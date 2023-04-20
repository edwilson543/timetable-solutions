# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestLogin(TestClient):
    def test_login_approved_user(self):
        user = data_factories.create_user_with_known_password(password="password")
        data_factories.Profile(user=user, approved_by_school_admin=True)

        # Navigate to the login page
        url = UrlName.LOGIN.url()
        login_page = self.client.get(url)

        # Check response ok
        assert login_page.status_code == 200

        # Attempt a login with some valid details
        login_form = login_page.forms["login-form"]
        login_form["username"] = user.username
        login_form["password"] = "password"

        response = login_form.submit()

        # Check the user was logged in and redirected to their dashboard
        assert response.status_code == 302
        assert response.location == UrlName.DASHBOARD.url()

    def test_login_unapproved_user(self):
        user = data_factories.create_user_with_known_password(password="password")
        data_factories.Profile(user=user, approved_by_school_admin=False)

        # Navigate to the login page
        url = UrlName.LOGIN.url()
        login_page = self.client.get(url)

        # Check response ok
        assert login_page.status_code == 200

        # Attempt a login with some valid details
        login_form = login_page.forms["login-form"]
        login_form["username"] = user.username
        login_form["password"] = "password"

        response = login_form.submit()

        # Check user gets a not yet approved error
        assert response.status_code == 200
        errors = response.context["form"].errors.as_text()
        assert "Your account has not yet been approved" in errors

    def test_attempt_login_with_invalid_credentials(self):
        # Navigate to the login page
        url = UrlName.LOGIN.url()
        login_page = self.client.get(url)

        # Check response ok
        assert login_page.status_code == 200

        # Attempt a login with some invalid details
        login_form = login_page.forms["login-form"]
        login_form["username"] = "fake_user"
        login_form["password"] = "fake_password123"

        response = login_form.submit()

        # Check user gets invalid credentials error
        assert response.status_code == 200
        errors = response.context["form"].errors.as_text()
        assert "Please enter a correct username and password" in errors

    def test_attempt_login_with_incomplete_registration_redirects_to_relevant_step(
        self,
    ):
        user = data_factories.create_user_with_known_password(password="password")

        # Navigate to the login page
        url = UrlName.LOGIN.url()
        login_page = self.client.get(url)

        # Check response ok
        assert login_page.status_code == 200

        # Attempt a login with some valid details
        login_form = login_page.forms["login-form"]
        login_form["username"] = user.username
        login_form["password"] = "password"

        response = login_form.submit()

        # Check the user was logged in but redirected to the registration pivot
        assert response.status_code == 302
        assert response.location == UrlName.REGISTER_PIVOT.url()
