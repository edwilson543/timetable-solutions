"""
Views for managing user passwords.
"""

# Django imports
from django import http
from django.contrib import messages
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import views as auth_views

# Local application imports
from interfaces.constants import UrlName


class PasswordChange(auth_views.PasswordChangeView):
    success_url = UrlName.DASHBOARD.url(lazy=True)

    def form_valid(self, form: auth_forms.PasswordChangeForm) -> http.HttpResponse:
        message = "Your password has been updated!"
        messages.success(request=self.request, message=message)
        return super().form_valid(form=form)
