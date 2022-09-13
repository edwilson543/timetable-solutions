# Django imports
from django.urls import include, re_path, path

# Local application imports
from .views import Register, SchoolRegisterPivot, SchoolRegistration, ProfileRegistration, custom_logout, dashboard_view

urlpatterns = [
    re_path(r"^accounts/", include("django.contrib.auth.urls")),
    re_path(r"^logout", custom_logout, name="logout"),
    re_path(r"^dashboard/", dashboard_view, name="dashboard"),
    path("register/", Register.as_view(), name="register"),
    path("register/pivot/", SchoolRegisterPivot.as_view(), name="registration_pivot"),
    path("register/pivot/school_id/", SchoolRegistration.as_view(), name="school_registration"),
    path("register/pivot/profile/", ProfileRegistration.as_view(), name="profile_registration"),
]
