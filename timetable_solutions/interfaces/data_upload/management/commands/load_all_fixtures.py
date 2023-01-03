"""
Module containing custom management command for loading in fixtures, so there is some data available to use.
"""

# Django imports
from django.core import management


class Command(management.base.BaseCommand):
    """
    Command used to load in all initial fixtures to the database.
    Note that we build this command using existing django management commands.
    Note also that this command involves FLUSHING all data currently in the database.
    """

    help = "Command to load in all fixtures providing initial data for the application, and in the correct order."

    def add_arguments(self, parser: management.CommandParser) -> None:
        """
        Method adding arguments to the command.
        arg: --include_solution - whether to load in the Lesson
        """
        parser.add_argument(
            "--include_solution",
            action="store_true",  # store_true stores the arg as a boolean
            help="Include if you also want to pre-populate a solution for the test dataset.",
        )

    def handle(self, *args: str, **kwargs: str) -> None:
        """
        Method carrying out the processing relevant to this command
        """
        management.call_command(
            "loaddata", "user_school_profile.json"
        )  # All other models depend on this fixture
        management.call_command("loaddata", "year_groups.json")
        management.call_command("loaddata", "classrooms.json")
        management.call_command("loaddata", "pupils.json")
        management.call_command("loaddata", "teachers.json")
        management.call_command("loaddata", "timetable.json")

        if kwargs["include_solution"]:  # store_true ensures this is always present
            management.call_command("loaddata", "lessons_with_solution.json")
        else:
            management.call_command("loaddata", "lessons_without_solution.json")

        self.stdout.write(self.style.SUCCESS(f"Successfully loaded in all fixtures!"))
