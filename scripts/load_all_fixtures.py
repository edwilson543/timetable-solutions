"""
Script to load all fixtures into the database in the correct order, so that there is something to view on the site.
A data migration is not used, to automatically include all data fixtures into the database, because this is not wanted
for the tests.
"""

# Django imports
from django.core.management import call_command


def load_initial_data():
    """Function to load in the initial data from the JSON fixtures, in the correct order"""
    call_command("loaddata", "user_school_profile.json")  # All other models depend on this fixture
    call_command("loaddata", "classrooms.json")
    call_command("loaddata", "pupils.json")
    call_command("loaddata", "teachers.json")
    call_command("loaddata", "timetable.json")
    call_command("loaddata", "fixed_classes.json")  # This fixture depends on the installation of all other fixtures


if __name__ == "__main__":
    load_initial_data()
