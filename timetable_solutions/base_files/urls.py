"""
Base url stubs for the timetable solutions project.
"""

# Django imports
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.views import generic

# Local application imports
from interfaces.constants import UrlName
from interfaces.custom_admin.admin.custom_admin_site import user_admin


urlpatterns = (
    [
        path("", generic.RedirectView.as_view(url=reverse_lazy(UrlName.LOGIN.value))),
        path("empty/", generic.TemplateView.as_view(template_name="new-base.html")),
        path("view/", include("interfaces.view_timetables.urls")),
        path("data/", include("interfaces.data_management.urls")),
        path("create/", include("interfaces.create_timetables.urls")),
        path("users/", include("interfaces.users.urls")),
        path("admin/", admin.site.urls),
        path("data/admin/", user_admin.urls),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
