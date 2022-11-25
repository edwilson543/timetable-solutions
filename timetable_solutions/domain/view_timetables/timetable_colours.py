"""
Module defining the constant values (hexadecimal colour codes) assigned to subject names, and logic for using these.
"""

# Standard library imports
from enum import StrEnum
import re
from typing import Dict, Pattern

# Third party imports
import pandas as pd

# Local application imports
from data import models


class TimetableColourAssigner:
    """
    Class used to assign hexadecimal colours to different period names, for colour coding the timetables in the UI
    when rendering a pupil / teacher's timetable.
    """
    class Colour(StrEnum):
        """
        Generic period type colours - for certain period types a specific colour is given,
        otherwise, we assign colours based on the most periods / week.
        """
        MEAL = "#b3b3b3"  # Light grey
        BREAK = "#bfbfbf"  # Slightly darker grey
        FREE = "#feffba"  # Yellow

    # Dictionary with compiled regex patterns as keys (matched against user input strings), and values are colour codes
    _regex_dict: Dict[Pattern, Colour] = {
        re.compile("(.*breakfast.*)|(.*lunch.*)|(.*tea.*)|(.*dinner.*)|(.*supper.*)",
                   flags=re.IGNORECASE): Colour.MEAL.value,
        re.compile("(.*break.*)|(.*recreation.*)|(.*play.*time.*)", flags=re.IGNORECASE): Colour.BREAK.value,
        re.compile("(.*free.*)|(.*empty.*)|(.*spare.*)", flags=re.IGNORECASE): Colour.FREE.value,
    }

    # Colours to be assigned to subjects, based on weekly frequency in pupil timetables,
    # or in the case of teacher timetables, the numbers represent year groups.
    _colour_ranking: Dict[int, Colour] = {
        0: "#ffbfd6",  # Pale red
        1: "#c8d4e3",  # Pale blue
        2: "#b3f2b3",  # Pale green
        3: "#d0bad6",  # Lilac
        4: "#e3ad62",  # Pale orange
        5: "#675fb0",  # Dark blue
        6: "#aabf5e",  # Muddy green
        7: "#8f7e78",  # Pink-grey
        8: "#d18771",  # Dark red
        9: "#169c6f",  # Turquoise
        10: "#c9ae61",  # Light brown
    }

    @classmethod
    def get_colours_for_pupil_timetable(cls, lessons: models.LessonQuerySet) -> Dict[str, str]:
        """
        Method to produce a dictionary mapping a single pupil's subject name strings to hexadecimal colours.
        :param lessons - the queryset of lessons that a given pupil takes
        :return A dictionary whose keys are subject names, and values are corresponding hexadecimal colour codes
        """
        # Get dictionary of  subject_name -> hexadecimal colour mappings
        generic_period_colours = cls._get_generic_period_colours(lessons=lessons)

        # Count the instances of each subject per week, removing any that are already in lesson_colours
        uncleaned_lesson_counts = {lesson.subject_name: lesson.total_required_slots for lesson in lessons}
        lesson_counts = {subject_name: count for subject_name, count in uncleaned_lesson_counts.items() if
                         subject_name not in generic_period_colours.keys()}

        # Rank the lessons ensuring all final ranks are in the specified colour ranking
        counts_ser = pd.Series(lesson_counts)  # Series used to access the .rank() method
        rank_ser = counts_ser.rank(method="first", ascending=False) - 1  # -1 so that ranks start at 0
        max_defined_rank = max(cls._colour_ranking.keys())
        rank_ser = rank_ser.mod(max_defined_rank)
        lesson_rank_dict = rank_ser.to_dict()

        # Assign each subject a colour based on rank
        ranked_colours = {subject_name: cls._colour_ranking[rank] for subject_name, rank in lesson_rank_dict.items()}
        lesson_colours = {**generic_period_colours, **ranked_colours}
        return lesson_colours

    @classmethod
    def get_colours_for_teacher_timetable(cls, lessons: models.LessonQuerySet) -> Dict[str | int, str]:
        """
        Method to produce a dictionary mapping a single teacher's year groups, and year-group-less lessons (lunch /
        break) name strings to hexadecimal colours.
        :param lessons - the queryset of lessons that a given teacher teaches / has
        :return A dictionary whose keys are subject names, and values are corresponding hexadecimal colour codes
        """
        # Get dictionary of  subject_name -> hexadecimal colour mappings
        generic_period_colours = cls._get_generic_period_colours(lessons=lessons)

        colour_ranking = cls._colour_ranking
        year_group_colours = {}  # Dictionary that will map year group colours -> ints
        for lesson in lessons:
            all_pupils = lesson.pupils.all()
            if all_pupils.exists():  # Take first pupil from queryset since all have same year group
                first_pupil = lesson.pupils.all().first()
                year_group: int = first_pupil.year_group
                year_group_colours[year_group] = colour_ranking[year_group]

        all_colours = {**generic_period_colours, **year_group_colours}
        return all_colours

    # HELPER METHODS
    @classmethod
    def _get_generic_period_colours(cls, lessons: models.LessonQuerySet) -> Dict[str, str]:
        """
        Method getting the generic period colours relevant to an individual timetable.
        :param lessons - the queryset of lessons specific to an individual pupil / teacher
        :return generic_period_colours -  dictionary of subject_name: hexadecimal_colour_codes, where the subject names
        correspond to the generic period types identified in the lessons parameter
        """
        generic_period_colours = {
            lesson.subject_name: matched_colour_code for lesson in lessons if
            (matched_colour_code := cls.check_lesson_for_colour_in_regex(lesson_name=lesson.subject_name)) is not None
        }
        # Free periods are normally undefined (i.e. will NOT be in the lessons arg), and are used to fill missing slots
        # So this must be added manually
        generic_period_colours[cls.Colour.FREE.name] = cls.Colour.FREE.value
        return generic_period_colours

    @classmethod
    def check_lesson_for_colour_in_regex(cls, lesson_name: str) -> Colour | None:
        """
        Method to check the lesson_name parameter to see if it matches any of the regexes in regex dict.
        :return the colour code from the matched regex, if there is one, otherwise None.

        Note - we actually use the method to help count the subjects that aren't of generic type in the
        timetable_summary_stats.py. Not really what it was intended for, but it does a job...
        """
        for regex, colour_code in cls._regex_dict.items():
            is_match = bool(re.search(regex, string=lesson_name))
            if is_match:
                return colour_code
