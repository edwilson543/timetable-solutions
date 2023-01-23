# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from domain.view_timetables.timetable_component import TimetableComponent
from tests import domain_factories


class TestTimetableComponent:
    """Unit tests on the TimetableComponent class"""

    # --------------------
    # Properties
    # --------------------

    @pytest.mark.parametrize(
        "starts_at,ends_at,expected_duration",
        [
            (dt.time(hour=8), dt.time(hour=9), 1),
            (dt.time(hour=9, minute=30), dt.time(hour=10, minute=15), 0.75),
        ],
    )
    def test_duration_hours(self, starts_at, ends_at, expected_duration):
        """Test the correct duration is computed."""
        component = domain_factories.TimetableComponent(
            starts_at=starts_at, ends_at=ends_at
        )

        assert component.duration_hours == expected_duration
