"""Module containing custom management command for loading in fixtures."""

# Django imports
from django.core.management import base
from django.core.management import call_command


# TODO move commands into their own django app (probably in a new layer)
# TODO write tests for this command - with and without inc. fixed classes


class Command(base.BaseCommand):
    """
    Command used to load in all initial fixtures to the database.
    Note that we build this command using existing django management commands.
    Note also that this command involves FLUSHING all data currently in the database.
    """

    help = "Command to load in all fixtures providing initial data for the application, and in the correct order."

    def add_arguments(self, parser):
        """
        Method adding arguments to the command.
        arg: --inc_fixed_classes - there is a Fixture containing a mock solver solution, which we may not always want
        to load in by default
        :arg: --runserver - whether or not to immediately run the django server after loading in the fixtures
        """
        parser.add_argument("--include_fixed_classes", action="store_true",  # store_true stores the arg as a boolean
                            help="Include this argument if you also want to pre-populate a timetable solution.")

    def handle(self, *args, **kwargs):
        """Method carrying out the processing relevant to this command"""

        call_command("flush", interactive=False)  # Reset the database

        call_command("loaddata", "user_school_profile.json")  # All other models depend on this fixture
        call_command("loaddata", "classrooms.json")
        call_command("loaddata", "pupils.json")
        call_command("loaddata", "teachers.json")
        call_command("loaddata", "timetable.json")
        call_command("loaddata", "unsolved_classes.json")
        call_command("loaddata", "fixed_classes_lunch.json")  # These are not solver-produced so always include

        if kwargs["include_fixed_classes"]:  # store_true ensures this is always present
            call_command("loaddata", "fixed_classes.json")

        self.stdout.write(self.style.SUCCESS(f"Successfully loaded in all fixtures!"))
