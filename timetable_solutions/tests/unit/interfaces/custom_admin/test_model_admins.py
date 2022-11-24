"""
Unit tests for the subclasses of the BaseModelAdmin class
"""

# Django imports
from django import test
from django import urls
from django.contrib.auth.models import User

# Local application imports
from data import models
from interfaces.custom_admin import admin


class TestBaseModelAdmin(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json", "fixed_classes_lunch.json",
                "test_scenario_1.json"]  # Included since we need some data not corresponding to access key 6

    def test_get_queryset_pupils(self):
        """
        Test that the queryset of pupils for a user of school 123456 is restricted to their school only.
        """
        # Set test parameters
        factory = test.RequestFactory()
        request = factory.get("/data/admin/data/pupil/")
        request.user = User.objects.get(username="dummy_teacher")

        # Execute test unit
        queryset = admin.PupilAdmin(model=models.Pupil, admin_site=admin.user_admin).get_queryset(request=request)

        # Check outcome
        expected_queryset = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        self.assertQuerysetEqual(queryset, expected_queryset, ordered=False)
