"""
Endpoint configuration for the rest api.
Note that currently the rest api is not wanted in production, so the urls patterns are only included conditionally.
No other components of the site depends on these urls, so it is fine.
"""

# Django imports
from django import urls
from django.conf import settings

# Third party imports
from rest_framework import routers

# Local application imports
from interfaces.rest_api import views


if settings.ENABLE_REST_API:
    router = routers.DefaultRouter()
    router.register(r"fixedclasses", viewset=views.FixedClass, basename="fixedclasses")
    router.register(r"unsolvedclasses", viewset=views.UnsolvedClass, basename="unsolvedclasses")
    router.register(r"timetableslots", viewset=views.TimetableSlot, basename="timetableslots")

    urlpatterns = [
        urls.path("", urls.include(router.urls))
    ]
else:
    urlpatterns = []
