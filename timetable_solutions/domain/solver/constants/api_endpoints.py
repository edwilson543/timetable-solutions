"""Module specifying where the solver (input data loader) should look for the relevant data"""

# Standard library imports
from dataclasses import dataclass


@dataclass
class DataLocation:
    """
    Dataclass creating and storing absolute urls to where each piece of data relevant to the solver is located.
    Domain name and protocol can be both set to '' for testing purposes.
    """
    school_access_key: int
    domain_name: str = "127.0.0.1:8000"  # Locally hosted for now
    protocol: str = "http"

    def __post_init__(self):
        """Construct the full urls from the passed data"""
        self.fixed_classes_url = f"{self.protocol}://{self.domain_name}/" \
                                 f"api/fixedclasses/?school_access_key={self.school_access_key}"
        self.unsolved_classes_url = f"{self.protocol}://{self.domain_name}" \
                                    f"/api/unsolvedclasses?school_access_key={self.school_access_key}"
        self.timetable_slots_url = f"{self.protocol}://{self.domain_name}" \
                                   f"/api/timetableslots?school_access_key={self.school_access_key}"
