# Local application imports
from interfaces.constants import UrlName
from tests.functional.client import TestClient


class TestDashboard(TestClient):
    def test_authenticated_user_can_access_dashboard(self):
        """
        Smoke test that the dashboard loads.
        """
        self.create_school_and_authorise_client()

        # Navigate to the dashboard
        url = UrlName.DASHBOARD.url()
        dashboard = self.client.get(url)

        # Check response ok
        assert dashboard.status_code == 200

    def test_not_authenticated_user_redirected_to_login(self):
        # Try navigating to the dashboard without first authenticating the client
        url = UrlName.DASHBOARD.url()
        login_redirect = self.client.get(url)

        # Check response ok
        assert login_redirect.status_code == 302
        assert UrlName.LOGIN.url() in login_redirect.location
