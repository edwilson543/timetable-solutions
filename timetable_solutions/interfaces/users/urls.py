# Django imports
from django.urls import include, path, re_path

# Local application imports
from interfaces.constants import UrlName

from . import htmx_views, views

urlpatterns = [
    # Views relating to authentication
    re_path(r"^accounts/login", views.CustomLogin.as_view(), name=UrlName.LOGIN.value),
    re_path("^accounts/logout", views.custom_logout, name=UrlName.LOGOUT.value),
    re_path("^accounts/", include("django.contrib.auth.urls")),
    path("dashboard/", views.dashboard, name=UrlName.DASHBOARD.value),
    # Views at each step of registration
    path("register/", views.Register.as_view(), name=UrlName.REGISTER.value),
    path(
        "register/pivot/",
        views.SchoolRegisterPivot.as_view(),
        name=UrlName.REGISTER_PIVOT.value,
    ),
    path(
        "register/pivot/school_id/",
        views.SchoolRegistration.as_view(),
        name=UrlName.SCHOOL_REGISTRATION.value,
    ),
    path(
        "register/pivot/profile/",
        views.ProfileRegistration.as_view(),
        name=UrlName.PROFILE_REGISTRATION.value,
    ),
    # HTMX views - registration
    path(
        "register/username/",
        htmx_views.username_field_view,
        name=UrlName.USERNAME_FIELD_REGISTRATION.value,
    ),
]
