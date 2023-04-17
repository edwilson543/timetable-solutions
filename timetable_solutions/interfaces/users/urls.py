# Django imports
from django.urls import include, path, re_path

# Local application imports
from interfaces.constants import UrlName
from interfaces.users import views

urlpatterns = [
    # Views relating to authentication
    re_path(r"^accounts/login", views.Login.as_view(), name=UrlName.LOGIN.value),
    re_path("^accounts/logout", views.custom_logout, name=UrlName.LOGOUT.value),
    re_path(
        "^accounts/password_change",
        views.PasswordChange.as_view(),
        name=UrlName.PASSWORD_CHANGE.value,
    ),
    re_path("^accounts/", include("django.contrib.auth.urls")),
    path("dashboard/", views.Dashboard.as_view(), name=UrlName.DASHBOARD.value),
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
]
