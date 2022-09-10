"""Module defining the model for a pupil and any ancillary objects."""

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School


class Pupil(models.Model):
    """Model for storing unique list of pupils."""

    class YearGroup(models.IntegerChoices):
        ONE = 1, "#b3f2b3"
        TWO = 2, "#ffbfd6"
        THREE = 3, "#c8d4e3"
        FOUR = 4, "#fcc4a2"
        FIVE = 5, "#babac2"

        @staticmethod
        def get_colour_from_year_group(year_group: int) -> str:
            """Method taking a year group name e.g. int: 1 and returning a hexadecimal colour e.g. #b3f2b3"""
            member = Pupil.YearGroup(year_group)
            return member.label

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    pupil_id = models.IntegerField()
    firstname = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    year_group = models.IntegerField(choices=YearGroup.choices)

    def __str__(self):
        """String representation of the model for the django admin site"""
        return f"{self.school}: {self.surname}, {self.firstname}"

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_id: int, pupil_id: int, firstname: str, surname: str, year_group: int):
        """Method to create a new Pupil instance."""
        pupil = cls.objects.create(school_id=school_id, pupil_id=pupil_id, firstname=firstname, surname=surname,
                                   year_group=year_group)
        return pupil
