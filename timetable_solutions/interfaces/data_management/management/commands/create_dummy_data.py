# Standard library imports
import datetime as dt

# Django imports
from django.contrib.auth import models as auth_models
from django.core.management import base as base_command
from django.db import transaction

# Local application imports
# The import from tests is a special-case, since it's a big shortcut
from data import constants, models
from tests import data_factories

# ---------------
# Constants
# ---------------

n_year_groups = 2

classes_per_year_group = 2

pupils_per_class = 10

lessons_per_week_per_teacher_classroom = 24

subject_lessons_per_week = {
    "Maths": 6,
    "English": 6,
    "History": 4,
    "Geography": 4,
    "Physics": 4,
    "Chemistry": 4,
    "French": 3,
    "Art": 3,
    "P.E.": 3,
}


class Command(base_command.BaseCommand):
    help = "Create some dummy data for a school when demonstrating or working with the site"

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

        with transaction.atomic():
            school = _create_school(school_access_key)
            # Create an admin user for this school if one does not exist already
            _create_admin_user_for_school(school)
            _create_extra_non_admin_users_for_school(school)

            # Create the school data
            _create_school_data(school)


def _create_school(school_access_key: int) -> models.School:
    """
    Create a school with the specified access key.
    """
    if models.School.objects.filter(school_access_key=school_access_key).exists():
        raise base_command.CommandError("School with this access key already exists")
    return data_factories.School(school_access_key=school_access_key)


def _create_admin_user_for_school(school: models.School) -> None:
    """
    Create some dummy user for the school.
    """
    if models.Profile.objects.filter(school=school).exists():
        return None

    # Try and give the new user the dummy_teacher username, otherwise append the school access key
    new_username = "dummy_teacher"
    dummy_teacher_exists = auth_models.User.objects.filter(
        username=new_username
    ).exists()
    if dummy_teacher_exists:
        new_username += str(school.school_access_key)

    user = data_factories.create_user_with_known_password(
        username=new_username, password="dt123dt123"
    )
    data_factories.Profile(
        user=user,
        school=school,
        role=constants.UserRole.SCHOOL_ADMIN,
        approved_by_school_admin=True,
    )


def _create_extra_non_admin_users_for_school(school: models.School) -> None:
    """
    Create some dummy users to populate the user admin part of the site.
    """
    for n in range(0, 100):
        user = data_factories.User()
        role = constants.UserRole.TEACHER if n % 2 else constants.UserRole.PUPIL
        data_factories.Profile(
            user=user, school=school, role=role, approved_by_school_admin=False
        )


def _create_school_data(school: models.School) -> None:
    """
    Create a complete set of school data.
    """
    _create_pupils_teachers_classrooms_lessons(school)
    _create_timetable_structure(school)


def _create_pupils_teachers_classrooms_lessons(school: models.School) -> None:
    """
    Create the core school data.
    """
    # Create some year groups
    year_groups = [
        data_factories.YearGroup(school=school) for _ in range(0, n_year_groups)
    ]

    # Create the exact number of teachers required
    teachers = {
        subject: [
            data_factories.Teacher(school=school)
            for _ in range(0, _get_n_teachers_classrooms_for_subject(subject))
        ]
        for subject, n_slots in subject_lessons_per_week.items()
    }

    # Create the exact number of classrooms required
    classrooms = {
        subject: [
            data_factories.Classroom(school=school, building=f"{subject} building")
            for _ in range(0, _get_n_teachers_classrooms_for_subject(subject))
        ]
        for subject, n_slots in subject_lessons_per_week.items()
    }

    # Create each year group
    iteration = 0
    for year_group in year_groups:
        # Within each year group, create some classes
        for class_id in range(0, classes_per_year_group):
            pupils = [
                data_factories.Pupil(school=school, year_group=year_group)
                for _ in range(0, pupils_per_class)
            ]

            # For each class, create the relevant lessons
            for subject, n_slots in subject_lessons_per_week.items():
                n_doubles = (n_slots - 1) // 2

                teacher_list = teachers[subject]
                teacher = teacher_list[iteration % len(teacher_list)]

                classroom_list = classrooms[subject]
                classroom = classroom_list[iteration % len(classroom_list)]

                data_factories.Lesson(
                    school=school,
                    lesson_id=f"{subject}-year-{year_group.year_group_id}-{class_id}",
                    subject_name=subject,
                    total_required_slots=n_slots,
                    total_required_double_periods=n_doubles,
                    pupils=pupils,
                    teacher=teacher,
                    classroom=classroom,
                )

                iteration += 1


def _create_timetable_structure(school: models.School) -> None:
    """
    Create the timetable slots and breaks for this school.
    """

    slots = [
        (dt.time(hour=8, minute=30), dt.time(hour=9, minute=15)),
        (dt.time(hour=9, minute=15), dt.time(hour=10)),
        (dt.time(hour=10), dt.time(hour=10, minute=45)),
        # Morning break
        (dt.time(hour=11, minute=15), dt.time(hour=12)),
        (dt.time(hour=12), dt.time(hour=12, minute=45)),
        # Lunch
        (dt.time(hour=13, minute=45), dt.time(hour=14, minute=30)),
        (dt.time(hour=14, minute=30), dt.time(hour=15, minute=15)),
        (dt.time(hour=15, minute=15), dt.time(hour=16)),
    ]

    breaks = [
        (dt.time(hour=10, minute=45), dt.time(hour=11, minute=15), "Morning break"),
        (dt.time(hour=12, minute=45), dt.time(hour=13, minute=45), "Lunch"),
    ]

    # Make the timetable relevant to all teachers and year groups
    teachers = models.Teacher.objects.all()
    year_groups = models.YearGroup.objects.all()

    for day_of_week in constants.Day.weekdays():
        for starts_at, ends_at in slots:
            data_factories.TimetableSlot(
                school=school,
                starts_at=starts_at,
                ends_at=ends_at,
                day_of_week=day_of_week,
                relevant_year_groups=year_groups,
            )
        for starts_at, ends_at, break_name in breaks:
            data_factories.Break(
                school=school,
                starts_at=starts_at,
                ends_at=ends_at,
                day_of_week=day_of_week,
                break_name=break_name,
                relevant_year_groups=year_groups,
                teachers=teachers,
            )


def _get_n_teachers_classrooms_for_subject(subject: str) -> int:
    """
    Get the required number of teachers / classrooms at the school.
    """
    slots_per_class_per_week = subject_lessons_per_week[subject]
    minimum_requirement = int(
        slots_per_class_per_week
        * n_year_groups
        * classes_per_year_group
        / lessons_per_week_per_teacher_classroom
    )
    return max(minimum_requirement, 1)
