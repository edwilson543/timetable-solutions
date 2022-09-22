"""Module specifying where the solver (input data loader) should look for the relevant data"""

# Standard library imports
from dataclasses import dataclass


@dataclass
class DataLocation:
    """Dataclass creating and storing absolute urls to where each piece of data relevant to the solver is located."""
    school_access_key: int
    domain_name: str = "http://127.0.0.1:8000/"

    def __post_init__(self):
        self.fixed_classes_url = f"{self.domain_name}/api/fixedclasses/?school_access_key={self.school_access_key}"
        self.unsolved_classes_url = f"{self.domain_name}/api/unsolvedclasses?school_access_key={self.school_access_key}"
        self.timetable_slots_url = f"{self.domain_name}/api/timetableslots?school_access_key={self.school_access_key}"
