"""
Module defining the constant values (hexadecimal colour codes) assigned to subject names, and logic for using these.
"""

# Standard library imports
from enum import Enum
import re
from typing import Dict, Union, Pattern

# Third party imports
import pandas as pd

# Local application imports
from data import models


class TimetableColour(Enum):
    """
    Enumeration of the hexadecimal colours to use for colour coding the timetables in the UI. For certain period types
    (meals / free), a specific colour is given, otherwise, we assign colours based on the most periods / week.

    The class also has methods defining the logic to assign the colour codes to use when rendering a pupil / teacher's
    timetable, to school class name strings
    """
    # Generic period type colours - assigned using the regex dict defined below
    MEAL = "#b3b3b3"  # Light grey
    BREAK = "#bfbfbf"  # Slightly darker grey
    FREE = "#feffba"  # Yellow

    @staticmethod
    def _get_colour_ranking() -> Dict[int, str]:
        """
        Method returning a constant dictionary (equivalently an enum.property in python 3.11, where as this project uses
        python 3.8)
        :return: Ranked subject colours - to be assigned to subjects, based on weekly frequency in pupil timetables,
        or in the case of teacher timetables, the numbers represent year groups.
        """
        colour_ranking = {
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
        return colour_ranking

    @classmethod
    def _get_regex_dict(cls) -> Dict[Pattern[str], str]:
        """
        Method returning a constant dictionary (equivalently an enum.property in python 3.11, where as this project uses
        python 3.8)
        :return dictionary whose keys are compiled regex patterns, and the values are colour codes
        (accessed via the Enum member values). This dict is used to match against user input strings, to see if any of
        their input classes should be assigned a default colour
        """
        regex_dict = {
            re.compile("(.*breakfast.*)|(.*lunch.*)|(.*tea.*)|(.*dinner.*)|(.*supper.*)",
                       flags=re.IGNORECASE): cls.MEAL.value,
            re.compile("(.*break.*)|(.*recreation.*)|(.*play.*time.*)", flags=re.IGNORECASE): cls.BREAK.value,
            re.compile("(.*free.*)|(.*empty.*)|(.*spare.*)", flags=re.IGNORECASE): cls.FREE.value,
        }
        return regex_dict

    @classmethod
    def get_colours_for_pupil_timetable(cls, classes: models.FixedClassQuerySet) -> Dict[str, str]:
        """
        Method to produce a dictionary mapping a single pupil's subject name strings to hexadecimal colours.
        :param classes - the queryset of classes that a given pupil takes
        :return A dictionary whose keys are subject names, and values are corresponding hexadecimal colour codes
        """
        # Create dictionary of fixed period name -> hexadecimal colour mappings
        generic_period_colours = cls._get_generic_period_colours(classes=classes)

        colour_ranking = cls._get_colour_ranking()  # To be used throughout remainder of method

        # Count the instances of each subject per week, removing any that are already in class_colours
        uncleaned_class_counts = {klass.subject_name: klass.time_slots.all().count() for klass in classes}
        class_counts = {subject_name: count for subject_name, count in uncleaned_class_counts.items() if
                        subject_name not in generic_period_colours.keys()}

        # Rank the classes ensuring all final ranks are in the specified colour ranking
        counts_ser = pd.Series(class_counts)  # Series used to access the .rank() method
        rank_ser = counts_ser.rank(method="first", ascending=False) - 1  # -1 so that ranks start at 0
        max_defined_rank = max(colour_ranking.keys())
        rank_ser = rank_ser.mod(max_defined_rank)
        class_rank_dict = rank_ser.to_dict()

        # Assign each subject a colour based on rank
        ranked_colours = {subject_name: colour_ranking[rank] for subject_name, rank in class_rank_dict.items()}
        class_colours = {**generic_period_colours, **ranked_colours}
        return class_colours

    @classmethod
    def get_colours_for_teacher_timetable(cls, classes: models.FixedClassQuerySet) -> Dict[Union[str, int], str]:
        """
        Method to produce a dictionary mapping a single teacher's year groups, and year-group-less classes (lunch /
        break) name strings to hexadecimal colours.
        :param classes - the queryset of classes that a given teacher teaches / has
        :return A dictionary whose keys are subject names, and values are corresponding hexadecimal colour codes
        """
        # Create dictionary of fixed period name -> hexadecimal colour mappings
        generic_period_colours = cls._get_generic_period_colours(classes=classes)

        colour_ranking = cls._get_colour_ranking()
        year_group_colours = {}  # Dictionary that will map year group colours -> ints
        for klass in classes:
            all_pupils = klass.pupils.all()
            if all_pupils.exists():  # Take first pupil from queryset since all have same year group
                first_pupil = klass.pupils.all().first()
                year_group: int = first_pupil.year_group
                year_group_colours[year_group] = colour_ranking[year_group]

        all_colours = {**generic_period_colours, **year_group_colours}
        return all_colours

    # HELPER METHODS
    @classmethod
    def _get_generic_period_colours(cls, classes: models.FixedClassQuerySet) -> Dict[str, str]:
        """
        Method getting the generic period colours relevant to an individual timetable.
        :param classes - the queryset of classes specific to an individual pupil / teacher
        :return generic_period_colours -  dictionary of subject_name: hexadecimal_colour_codes, where the subject names
        correspond to the generic period types identified in the classes parameter
        """
        generic_period_colours = {
            klass.subject_name: matched_colour_code for klass in classes if
            (matched_colour_code := cls._check_class_for_colour_in_regex(class_name=klass.subject_name)) is not None
        }
        # Free periods are normally undefined (i.e. will NOT be in the classes arg), and are used to fill missing slots
        # So this must be added manually
        generic_period_colours[cls.FREE.name] = cls.FREE.value
        return generic_period_colours

    @classmethod
    def _check_class_for_colour_in_regex(cls, class_name: str) -> Union[str, None]:
        """
        Method to check the class_name parameter to see if it matches any of the regexes in regex dict.
        :return the colour code from the matched regex, if there is one, otherwise None.
        """
        regex_dict = cls._get_regex_dict()
        for regex, colour_code in regex_dict.items():
            is_match = bool(re.search(regex, string=class_name))
            if is_match:
                return colour_code
