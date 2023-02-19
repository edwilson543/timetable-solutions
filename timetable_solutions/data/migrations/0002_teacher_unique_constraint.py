# Generated by Django 4.1.2 on 2023-02-19 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="teacher",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="teacher",
            constraint=models.UniqueConstraint(
                models.F("school"),
                models.F("teacher_id"),
                name="teacher_id_unique_for_school",
            ),
        ),
    ]
