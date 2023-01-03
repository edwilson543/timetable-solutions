# Generated by Django 4.1.2 on 2023-01-03 07:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0002_squashed"),
    ]

    operations = [
        migrations.CreateModel(
            name="YearGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("year_group", models.CharField(max_length=20)),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data.school"
                    ),
                ),
            ],
        ),
    ]
