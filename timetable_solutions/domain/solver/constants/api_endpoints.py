"""Module specifying where the solver (input data loader) should look for the relevant data"""

# Standard library imports
from dataclasses import dataclass


@dataclass
class DataLocation:
    """
    Dataclass creating and storing absolute urls to where each piece of data relevant to the solver is located.
    Protocol and domain name can be both set to '' for testing purposes.
    """
    school_access_key: int
    protocol_domain: str = "http://127.0.0.1:8000"  # Locally hosted for now

    def __post_init__(self):
        """Construct the full urls from the passed data"""
        self.fixed_classes_url = f"{self.protocol_domain}/api/fixedclasses/?school_access_key={self.school_access_key}"
        self.unsolved_classes_url = f"{self.protocol_domain}/api/" \
                                    f"unsolvedclasses?school_access_key={self.school_access_key}"
        self.timetable_slots_url = f"{self.protocol_domain}/api/" \
                                   f"timetableslots?school_access_key={self.school_access_key}"
