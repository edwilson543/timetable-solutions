# Django imports
from django import urls

# Third party imports
from rest_framework import routers

# Local application imports
from interfaces.api_to_solver import views


router = routers.DefaultRouter()
router.register(r"fixedclasses", viewset=views.FixedClass, basename="fixedclasses")

urlpatterns = [
    urls.path("", urls.include(router.urls))
]
