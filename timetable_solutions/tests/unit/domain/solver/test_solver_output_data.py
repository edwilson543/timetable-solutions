"""Unit tests for the TimetableSolverInputs class"""

# Django imports
from django import test

# Local application imports
from data import models
from domain.solver import linear_programming as lp


class TestTimetableSolverInputsLoading(test.TestCase):
    """
    Note that we use the LiveServerTestCase since the solver is effectively (designed to be possible to be) outside of
    this repository and thus uses the requests module to POST to the REST API.
    Therefore we need a full url to pass to requests.post()
    """

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json", "unsolved_classes.json"]

    pass
