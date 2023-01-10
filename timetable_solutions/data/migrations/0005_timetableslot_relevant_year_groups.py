# Generated by Django 4.1.2 on 2023-01-06 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0004_pupil_yeargroup_fk"),
    ]

    operations = [
        migrations.AddField(
            model_name="timetableslot",
            name="relevant_year_groups",
            field=models.ManyToManyField(related_name="slots", to="data.yeargroup"),
        ),
    ]
