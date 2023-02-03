"""
Base url stubs for the timetable solutions project.
"""

# Django imports
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView

# Local application imports
from interfaces.constants import UrlName
from interfaces.custom_admin.admin.custom_admin_site import user_admin

urlpatterns = (
    [
        path("", RedirectView.as_view(url=reverse_lazy(UrlName.LOGIN.value))),
        path("view/", include("interfaces.view_timetables.urls")),
        path("data/", include("interfaces.data_upload.urls")),
        path("create/", include("interfaces.create_timetables.urls")),
        path("users/", include("interfaces.users.urls")),
        path("admin/", admin.site.urls),
        path("data/admin/", user_admin.urls),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
