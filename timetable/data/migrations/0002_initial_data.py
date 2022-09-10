"""
Data migration to automatically include all data fixtures into the database so that there is something to view on the sit
"""

# Django imports
from django.core.management import call_command
from django.db import migrations


def load_initial_data(*args, **kwargs):
    """Function to load in the initial data from the JSON fixtures, in the correct order"""
    call_command("loaddata", "user_school_profile.json")  # All other models depend on this fixture
    call_command("loaddata", "classrooms.json")
    call_command("loaddata", "pupils.json")
    call_command("loaddata", "teachers.json")
    call_command("loaddata", "timetable.json")
    call_command("loaddata", "fixed_classes.json")  # This fixture depends on the installation of all other fixtures


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_initial_data)
    ]