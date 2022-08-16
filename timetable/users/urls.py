from django.urls import include, re_path
from django.views.generic import TemplateView
from .views import Register, SchoolRegisterPivot, SchoolRegistration, ProfileRegistration

urlpatterns = [
    re_path(r"^accounts/", include("django.contrib.auth.urls")),
    re_path(r"^dashboard/", TemplateView.as_view(template_name="users/dashboard.html"), name="dashboard"),
    re_path(r"^register/", Register.as_view(), name="register"),
    re_path(r"^register/pivot/", SchoolRegisterPivot.as_view(), name="registration_pivot"),
    re_path(r"^register/pivot/school/", SchoolRegistration.as_view(), name="school_registration"),
    re_path(r"^register/pivot/profile/", ProfileRegistration.as_view(), name="profile_registration"),
]
