# Django imports
from django.core.management import base as base_command

# Local application imports
from data import models
from domain import solver


class Command(base_command.BaseCommand):
    help = "Create timetable solutions for some school"

    def add_arguments(self, parser: base_command.CommandParser) -> None:
        parser.add_argument(
            "--school-access-key",
            help="The school that the dummy data should be created for",
        )

    def handle(self, *args: str, **options: str | int) -> None:
        if not (school_access_key := options["school_access_key"]):
            raise base_command.CommandError("You must provide a school access key")

        # Retrieve the school we are making the data for
        try:
            school_access_key = int(school_access_key)
        except ValueError:
            raise base_command.CommandError("School access key must be an integer")

        school = _get_school(school_access_key=school_access_key)

        # This is just a quick command for local dev purposes
        spec = solver.SolutionSpecification(
            allow_split_lessons_within_each_day=False,
            allow_triple_periods_and_above=False,
        )

        solver.produce_timetable_solutions(
            school_access_key=school.school_access_key, solution_specification=spec
        )


def _get_school(school_access_key: int) -> models.School:
    """
    Get the school specified by the access key.
    """
    try:
        return models.School.objects.get(school_access_key=school_access_key)
    except models.School.DoesNotExist:
        raise base_command.CommandError("No school with this access key exists")
