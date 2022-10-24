"""
Module defining the logic that allows users to reset their data uploads (i.e. delete the data they have already
uploaded)
"""

# Standard library imports
from dataclasses import dataclass


@dataclass(frozen=True)
class UploadsToReset:
    """
    List options for resetting
    Instantiated by various views
    """
    Pupil: True
    pass


def reset_data(tables_to_reset: UploadsToReset):
    pass
