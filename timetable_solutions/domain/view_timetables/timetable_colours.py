"""
Module defining the constant values (hexadecimal colour codes) assigned to subject names, and logic for using these.
"""

# Standard library imports
from enum import Enum
from typing import Dict, Union

# Third party imports
import pandas as pd

# Local application imports
from data import models


class TimetableColour(Enum):
    """
    Enumeration of the hexadecimal colours to use for the timetables in the UI. For certain subject types
    (lunch / free), a specific colour is given, otherwise, we assign colours based on the most periods.

    We also use this enum to define the logic to assign the colours to use when rendering a pupil / teacher's timetable.
    """
    # Unranked subject colours
    LUNCH = "#b3b3b3"  # Light grey
    BREAK = "#bfbfbf"  # Slightly darker grey
    FREE = "#feffba"  # Yellow

    # Ranked subject colours - to be assigned to subjects, based on weekly frequency
    # Or in the case of teacher timetables, the numbers represent year groups
    COLOUR_RANKING = {
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
    def get_colours_for_pupil_timetable(cls, classes: models.FixedClassQuerySet) -> Dict[str, str]:
        """
        Method to produce a dictionary mapping a single pupil's subject name strings to hexadecimal colours.
        :param classes - the queryset of classes that a given pupil takes
        :return A dictionary whose keys are subject names, and values are corresponding hexadecimal colour codes
        """
        # Create dictionary of fixed period name -> hexadecimal colour mappings
        unranked_colours = cls._get_unranked_colours()

        # Count the instances of each subject per week, removing any that are already in class_colours
        uncleaned_class_counts = {klass.subject_name: klass.time_slots.all().count() for klass in classes}
        class_counts = {subject_name: count for subject_name, count in uncleaned_class_counts.items() if
                        subject_name not in unranked_colours.keys()}

        # Rank the classes ensuring all final ranks are in the specified colour ranking
        counts_ser = pd.Series(class_counts)  # Create a series to use the rank functionality
        rank_ser = counts_ser.rank(method="first", ascending=False) - 1  # -1 so that ranks start at 0
        max_defined_rank = max(cls.COLOUR_RANKING.value.keys())
        rank_ser = rank_ser.mod(max_defined_rank)
        class_rank_dict = rank_ser.to_dict()

        # Assign each subject a colour based on rank
        ranked_colours = {subject_name: cls.COLOUR_RANKING.value[rank] for
                          subject_name, rank in class_rank_dict.items()}
        class_colours = unranked_colours | ranked_colours
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
        unranked_colours = cls._get_unranked_colours()

        year_group_colours = {}  # Dictionary that will map year group colours -> ints
        for klass in classes:
            all_pupils = klass.pupils.all()
            if all_pupils.exists():  # Take first pupil from queryset since all have same year group
                first_pupil = klass.pupils.all().first()
                year_group: int = first_pupil.year_group
                year_group_colours[year_group] = cls.COLOUR_RANKING.value[year_group]

        all_colours = unranked_colours | year_group_colours
        return all_colours

    # HELPER METHODS
    @classmethod
    def _get_unranked_colours(cls) -> Dict[str, str]:
        """
        Method to get the dictionary of colours as subject_name: hexadecimal_colour_code, which are 'unranked', i.e.
        all colours that are not in the COLOUR_RANKING dictionary
        """
        unranked_colours = {colour.name: colour.value for colour in cls if colour is not cls.COLOUR_RANKING}
        return unranked_colours
