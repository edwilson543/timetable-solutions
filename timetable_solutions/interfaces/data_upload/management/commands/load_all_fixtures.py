"""
Module containing custom management command for loading in fixtures, so there is some data available to use.
"""

# Django imports
from django.core.management import base
from django.core.management import call_command


class Command(base.BaseCommand):
    """
    Command used to load in all initial fixtures to the database.
    Note that we build this command using existing django management commands.
    Note also that this command involves FLUSHING all data currently in the database.
    """

    help = "Command to load in all fixtures providing initial data for the application, and in the correct order."

    def add_arguments(self, parser) -> None:
        """
        Method adding arguments to the command.
        arg: --include_solution - whether to load in the Lesson
        """
        parser.add_argument("--include_solution", action="store_true",  # store_true stores the arg as a boolean
                            help="Include if you also want to pre-populate a solution for the test dataset.")

    def handle(self, *args, **kwargs) -> None:
        """
        Method carrying out the processing relevant to this command
        """
        call_command("loaddata", "user_school_profile.json")  # All other models depend on this fixture
        call_command("loaddata", "classrooms.json")
        call_command("loaddata", "pupils.json")
        call_command("loaddata", "teachers.json")
        call_command("loaddata", "timetable.json")

        if kwargs["include_solution"]:  # store_true ensures this is always present
            call_command("loaddata", "lessons_with_solution.json")
        else:
            call_command("loaddata", "lessons_without_solution.json")

        self.stdout.write(self.style.SUCCESS(f"Successfully loaded in all fixtures!"))
