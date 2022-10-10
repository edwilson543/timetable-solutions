# Django imports
from django import urls

# Third party imports
from rest_framework import routers

# Local application imports
from interfaces.rest_api import views


router = routers.DefaultRouter()
router.register(r"fixedclasses", viewset=views.FixedClass, basename="fixedclasses")
router.register(r"unsolvedclasses", viewset=views.UnsolvedClass, basename="unsolvedclasses")
router.register(r"timetableslots", viewset=views.TimetableSlot, basename="timetableslots")

urlpatterns = [
    urls.path("", urls.include(router.urls))
]
