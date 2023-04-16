# Standard library imports
from typing import Any

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
    """
    Test client used for all functional tests.
    """

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

    def create_school_and_authorise_client(self) -> models.School:
        """
        Create a school in the db and authorise the client.
        This helps reduce boilerplate code in tests.
        """
        school = data_factories.School()
        self.authorise_client_for_school(school)
        return school

    def authorise_client_for_school(self, school: models.School) -> None:
        """
        Helper method to authorise the test client as a user at the school.
        """
        user = auth_models.User.objects.create_user(
            username="testing", password="unhashed"
        )
        data_factories.Profile(user=user, school=school)
        self.client.set_user(user=user)

    def anonymize_user(self) -> None:
        """
        Ensure there is no user authorised on the test client.
        """
        self.client.set_user(user=None)

    def hx_get(self, url: str, **kwargs: Any) -> django_webtest.DjangoWebtestResponse:
        """
        Get a url as if by hx-get.
        """
        extra_headers = kwargs.pop("extra_headers", None)
        headers = self._get_htmx_headers(extra_headers=extra_headers)
        return self.client.get(url=url, headers=headers, **kwargs)

    def hx_post_form(
        self, form: webtest.Form, **kwargs: Any
    ) -> django_webtest.DjangoWebtestResponse:
        """
        Submit a form as if by hx-post.
        """
        extra_headers = kwargs.pop("extra_headers", None)
        headers = self._get_htmx_headers(extra_headers=extra_headers)
        # Set the method manually since the actual html uses hx-post, and then submit
        form.method = "POST"
        return form.submit(headers=headers, **kwargs)

    def hx_delete_form(
        self, url: str, form: webtest.Form, **kwargs: Any
    ) -> django_webtest.DjangoWebtestResponse:
        """
        Submit a form as if by hx-delete.
        """
        extra_headers = kwargs.pop("extra_headers", None)
        headers = self._get_htmx_headers(extra_headers=extra_headers)
        fields = form.submit_fields(**kwargs)
        if csrf_token := self.client.cookies["csrftoken"]:
            headers["X-CSRFToken"] = csrf_token
        return self.client.delete(url, params=fields, headers=headers, **kwargs)

    def _get_htmx_headers(
        self, extra_headers: dict[str, str] | None = None
    ) -> dict[str, str]:
        """
        Get the headers for an htmx request based on some kwargs.
        """
        headers = {"HX-Request": "true"}
        if csrf_token := self.client.cookies.get("csrftoken"):
            # A utility csrf token header is included on the <body> tag, so retrieve this
            headers["X-CSRFToken"] = csrf_token
        if extra_headers:
            headers = extra_headers | headers
        return headers

    @property
    def http_host(self) -> str:
        """
        Get the name of the webtest http post used during testing.
        """
        return self.client.extra_environ["HTTP_HOST"]
