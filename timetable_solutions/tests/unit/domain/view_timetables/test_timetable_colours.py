"""
Module containing unit tests for timetable_colours.py module in view_timetables subdirectory of the domain layer.
"""

# Django imports
from django.test import TestCase

# Local application imports
from data import models
from domain.view_timetables.timetable_colours import TimetableColourAssigner


class Test(TestCase):
    """
    Test class for the all functions in the data_pre_processing module of the view_timetables in the domain.
    """
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "lessons_with_solution"]

    def test_get_colours_for_pupil_timetable_returns_expected_colour_dictionary(self):
        """
        Unit test for the get_colours_for_pupil_timetable method on the TimetableColourAssigner Enum
        """
        # Set test parameters
        pupil = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=1)
        lessons = pupil.lessons.all()
        expected_colour_dict = {
            "LUNCH": "#b3b3b3", "FREE": "#feffba",  # Generic period colours
            "FRENCH": "#ffbfd6", "MATHS": "#c8d4e3", "ENGLISH": "#b3f2b3",  # Ranked colours
        }

        # Execute test unit
        colours_dict = TimetableColourAssigner.get_colours_for_pupil_timetable(lessons=lessons)

        # Check outcome
        assert colours_dict == expected_colour_dict

    def test_get_colours_for_teacher_timetable_returns_expected_colour_dictionary(self):
        """
        Unit test for the get_colours_for_pupil_timetable method on the TimetableColourAssigner Enum
        """
        # Set test parameters
        teacher = models.Teacher.objects.get_individual_teacher(school_id=123456, teacher_id=1)
        lessons = teacher.lessons.all()
        expected_colour_dict = {
            "LUNCH": "#b3b3b3", "FREE": "#feffba",  # Generic period colours
            1: "#c8d4e3", 2: "#b3f2b3",  # Ranked colours
        }

        # Execute test unit
        colours_dict = TimetableColourAssigner.get_colours_for_teacher_timetable(lessons=lessons)

        # Check outcome
        assert colours_dict == expected_colour_dict

    # TESTS FOR HELPER METHODS
    def test_get_generic_period_colours(self):
        """
        Unit test for the method returning the generic period colour dictionary
        """
        # Set test parameters - in practice lessons would be for an individual pupil / teacher, below we use all
        models.Lesson.create_new(
            school_id=123456, lesson_id="Morning break Y1", subject_name="Morning break",
            total_required_slots=1, total_required_double_periods=0
        )
        lessons = models.Lesson.objects.get_all_instances_for_school(school_id=123456)

        # Execute test unit
        generic_period_colours = TimetableColourAssigner._get_generic_period_colours(lessons=lessons)

        # Check outcome
        assert generic_period_colours == {"LUNCH": "#b3b3b3", "MORNING BREAK": "#bfbfbf",  # Morning break gets caps
                                          TimetableColourAssigner.Colour.FREE.name: "#feffba"}

    def test_check_lesson_for_colour_in_regex_successful_meal_time_match_expected(self):
        """
        Unit test that any string we expect to match with the regex used to colour code meal times is successful.
        """
        # Set test parameters
        meal_time_strings = [
            "BREAKFAST", "breakfast", "Breakfast", "Morning breakfast", "Pre-school breakfast",
            "LUNCH", "lunch", "Lunch", "LuNcH", "   Lunch ", "Lunchtime", "LUNCHTIME", "Luncheon",
            "TEA", "tea", "Tea",
            "DINNER", "dinner", "Dinner",
            "SUPPER", "supper", "Supper"
        ]

        # Execute test unit and check outcome
        for meal_time_string in meal_time_strings:
            colour_code = TimetableColourAssigner.check_lesson_for_colour_in_regex(lesson_name=meal_time_string)
            assert colour_code == TimetableColourAssigner.Colour.MEAL.value

    def test_check_lesson_for_colour_in_regex_successful_break_match_expected(self):
        """
        Unit test that any string we expect to match with the regex used to colour code break times is successful.
        """
        # Set test parameters
        break_time_strings = [
            "BREAK", "break", "Break", "Morning break", "Afternoon break", "Breaktime", "Year 4 break"
        ]

        # Execute test unit and check outcome
        for break_time_strings in break_time_strings:
            colour_code = TimetableColourAssigner.check_lesson_for_colour_in_regex(lesson_name=break_time_strings)
            assert colour_code == TimetableColourAssigner.Colour.BREAK.value

    def test_check_lesson_for_colour_in_regex_successful_free_period_match_expected(self):
        """
        Unit test that any string we expect to match with the regex used to colour code free periods is successful.
        """
        # Set test parameters
        free_period_strings = [
            "FREE", "free", "Free", "Free time", "Freetime", "Free period"
        ]

        # Execute test unit and check outcome
        for free_time_strings in free_period_strings:
            colour_code = TimetableColourAssigner.check_lesson_for_colour_in_regex(lesson_name=free_time_strings)
            assert colour_code == TimetableColourAssigner.Colour.FREE.value

    def test_check_lesson_for_colour_in_regex_unsuccessful_match_against_all_options(self):
        """
        Unit test that any string we expect to NOT match with ANY OF THE regexes used to provide default colours to
        certain subject types returns None from the _check_lesson_for_colour_in_regex.
        """
        # Set test parameters
        no_match_strings = [
            "MATHS", "maths", "Maths", "ENGLISH", "english", "English", "FRENCH", "french", "French",  # ETC. etc. Etc.
        ]

        # Execute test unit and check outcome
        for no_match_string in no_match_strings:
            colour_code = TimetableColourAssigner.check_lesson_for_colour_in_regex(lesson_name=no_match_string)
            assert colour_code is None
