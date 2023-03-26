# Third party imports
import django_webtest
import pytest
import webtest

# Django imports
from django.contrib.auth import models as auth_models

# Local application imports
from data import models
from tests import data_factories


@pytest.mark.django_db
class TestClient:
    """Test client to be used for all functional tests."""

    client: django_webtest.DjangoTestApp
    """
    Entrypoint for test functions to the wsgi application.
    HTTP requests are submitted as e.g. self.client.get(url).
    """

    @pytest.fixture(autouse=True)
    def _(self, django_app: django_webtest.DjangoTestApp) -> None:
        """
        Use the django_webtest pytest plugin to provide the test wsgi application,
        and take care of patching and unpatching settings.
        """
        self.client = django_app

    def authorise_client_for_school(self, school: models.School) -> None:
        """Helper method to authorise the test client as a user at the school."""
        user = auth_models.User.objects.create_user(
            username="testing", password="unhashed"
        )
        data_factories.Profile(user=user, school=school)
        self.client.set_user(user=user)

    def anonymize_user(self) -> None:
        """Ensure there is no user authorised on the test client."""
        self.client.set_user(user=None)

    @staticmethod
    def hx_post_form(
        form: webtest.Form, **kwargs: object
    ) -> django_webtest.DjangoWebtestResponse:
        """
        Submit a form as if by hx-post.
        """
        # Set the method manually since the actual html uses hx-post, and then submit
        form.method = "POST"
        return form.submit(headers={"HX-Request": "true"}, **kwargs)
