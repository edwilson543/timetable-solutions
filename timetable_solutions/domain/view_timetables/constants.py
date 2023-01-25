"""Constants relating to viewing timetables."""

# Standard library imports
import enum


# String variables
FREE = "Free"


class Colour(enum.StrEnum):
    """Colours for timetable components that are not lessons"""

    BREAK = "#b3b3b3"  # Light grey
    FREE = "#feffba"  # Yellow
