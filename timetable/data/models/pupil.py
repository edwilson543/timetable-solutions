from django.db import models

from data.models import School


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

    pupil_id = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    year_group = models.IntegerField(choices=YearGroup.choices)