"""
Views for logging users in and out.
"""

# Django imports
from django import http
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import login, logout
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

# Local application imports
from interfaces.constants import UrlName


class Login(auth_views.LoginView):
    """
    Add some extra rules to the login process.
    """

    def setup(self, request: http.HttpRequest, *args: object, **kwargs: object) -> None:
        """
        Log a user out if they visit the login page.
        """
        super().setup(request, *args, **kwargs)
        if request.user.is_authenticated:
            logout(request)

    def form_valid(self, form: auth_forms.AuthenticationForm) -> http.HttpResponse:
        user = form.get_user()
        if not hasattr(user, "profile"):
            # The user has not completed registration
            login(
                self.request, user, backend="django.contrib.auth.backends.ModelBackend"
            )
            return redirect(to=UrlName.REGISTER_PIVOT.url())
        elif user.profile.approved_by_school_admin:
            return super().form_valid(form)
        else:
            error_message = (
                "Your account has not yet been approved by your school's admin account.\n"
                "Please contact them directly to approve your account."
            )
            form.add_error(None, error_message)
            return super().form_invalid(form=form)


def custom_logout(request: http.HttpResponse) -> http.HttpResponseRedirect:
    """
    Redirect users to the login page when they log out.
    """
    if request.user.is_authenticated:
        logout(request)
    return redirect(UrlName.LOGIN.url())
