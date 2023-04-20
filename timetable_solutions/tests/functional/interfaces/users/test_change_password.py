# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestPasswordChange(TestClient):
    def test_can_change_password(self):
        user = data_factories.create_user_with_known_password(password="password")
        data_factories.Profile(user=user, approved_by_school_admin=True)
        self.client.set_user(user=user)

        # Navigate to the password change page
        url = UrlName.PASSWORD_CHANGE.url()
        password_change_page = self.client.get(url)

        # Check response ok
        assert password_change_page.status_code == 200

        # Attempt to make a valid password change
        password_change_form = password_change_page.form
        password_change_form["old_password"] = "password"
        password_change_form["new_password1"] = "something else 123"
        password_change_form["new_password2"] = "something else 123"

        response = password_change_form.submit()

        # Check the user's password was changed
        assert response.status_code == 302
        assert response.location == UrlName.DASHBOARD.url()

        user.check_password("something else 123")

    def test_cannot_change_password_if_new_passwords_dont_match(self):
        user = data_factories.create_user_with_known_password(password="password")
        data_factories.Profile(user=user, approved_by_school_admin=True)
        self.client.set_user(user=user)

        # Navigate to the password change page
        url = UrlName.PASSWORD_CHANGE.url()
        password_change_page = self.client.get(url)

        # Check response ok
        assert password_change_page.status_code == 200

        # Attempt to make an invalid password change, where the new passwords don't match
        password_change_form = password_change_page.form
        password_change_form["old_password"] = "password"
        password_change_form["new_password1"] = "something else 123"
        password_change_form["new_password2"] = "something different 123"

        response = password_change_form.submit()

        # Check the user's password was not changed
        assert response.status_code == 200
        assert response.context["form"].errors
        user.check_password("password")
