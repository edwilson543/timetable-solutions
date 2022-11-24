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

    # GET FORM TEST
    def test_get_form_excludes_school(self):
        """
        Test that when getting the add / change form for the Pupil model, the 'school' is not rpesented to the user.
        """
        # Set test parameters
        factory = test.RequestFactory()
        request = factory.get("/data/admin/data/pupil/")
        request.user = User.objects.get(username="dummy_teacher")
        pupil_admin = admin.PupilAdmin(model=models.Pupil, admin_site=admin.user_admin)

        # Execute test unit
        change_form = pupil_admin.get_form(request=request, change=True)
        add_form = pupil_admin.get_form(request=request, change=False)

        # Check outcome - specifically that "school" is NOT IN either of the forms' base_fields
        base_fields = change_form.base_fields | add_form.base_fields
        assert set(base_fields.keys()) == {"pupil_id", "firstname", "surname", "year_group"}

    # SAVE MODEL TESTs
    def test_save_model_auto_associates_user_school_with_pupil(self):
        """
        Test that when posting a form to the admin to add a Pupil, the school (carried on the user's profile)
        successfully gets added to the object by the save_model code.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = "/data/admin/data/pupil/add/"
        form_data = {"pupil_id": 7, "firstname": "test", "surname": "testson", "year_group": 1}

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check outcome
        self.assertRedirects(response=response, expected_url="/data/admin/data/pupil/")
        pupil = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=7)
        assert pupil.school.school_access_key == 123456

    # GET QUERYSET TESTS
    def test_get_queryset_pupils_filters_by_school(self):
        """
        Test that the queryset of pupils for a user of school 123456 is restricted to their school only.
        """
        # Set test parameters
        factory = test.RequestFactory()
        request = factory.get("/data/admin/data/pupil/")
        request.user = User.objects.get(username="dummy_teacher")
        pupil_admin = admin.PupilAdmin(model=models.Pupil, admin_site=admin.user_admin)

        # Execute test unit
        queryset = pupil_admin.get_queryset(request=request)

        # Check outcome
        expected_queryset = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        self.assertQuerysetEqual(queryset, expected_queryset, ordered=False)
