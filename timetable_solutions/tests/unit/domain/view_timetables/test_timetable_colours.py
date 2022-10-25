"""
Module containing unit tests for timetable_colours.py module in view_timetables subdirectory of the domain layer.
"""

# Django imports
from django.db.models import QuerySet
from django.test import TestCase

# Local application imports
from data import models
from domain.view_timetables.timetable_colours import TimetableColour


class Test(TestCase):
    """
    Test class for the all functions in the data_pre_processing module of the view_timetables in the domain.
    """
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json", "fixed_classes_lunch.json"]

    def test_get_colours_for_pupil_timetable_returns_expected_dictionary(self):
        """
        Unit test for the get_colours_for_pupil_timetable method on the TimetableColour Enum
        """
        # Set test parameters
        pupil = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=1)
        classes = pupil.classes.all()
        expected_colour_dict = {
            "LUNCH": "#b3b3b3", "BREAK": "#bfbfbf", "FREE": "#feffba",  # Unranked colours
            "FRENCH": "#ffbfd6", "MATHS": "#c8d4e3", "ENGLISH": "#b3f2b3",  # Ranked colours
        }

        # Execute test unit
        colours_dict = TimetableColour.get_colours_for_pupil_timetable(classes=classes)

        # Check outcome
        assert colours_dict == expected_colour_dict

    def test_get_unranked_colours(self):
        """
        Unit test for the method returning the unranked colours stored on the TimetableColour Enum
        """
        # Execute test unit
        unranked_colours = TimetableColour.get_unranked_colours()

        # Check outcome
        assert unranked_colours == {"LUNCH": "#b3b3b3", "BREAK": "#bfbfbf", "FREE": "#feffba"}
