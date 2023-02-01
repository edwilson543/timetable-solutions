# Generated by Django 4.1.2 on 2023-01-23 08:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="School",
            fields=[
                (
                    "school_access_key",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("school_name", models.CharField(max_length=50)),
            ],
        ),
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
            options={
                "ordering": ["year_group"],
                "unique_together": {("school", "year_group")},
            },
        ),
        migrations.CreateModel(
            name="TimetableSlot",
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
                ("slot_id", models.IntegerField()),
                (
                    "day_of_week",
                    models.SmallIntegerField(
                        choices=[
                            (1, "Monday"),
                            (2, "Tuesday"),
                            (3, "Wednesday"),
                            (4, "Thursday"),
                            (5, "Friday"),
                            (6, "Saturday"),
                            (7, "Sunday"),
                        ]
                    ),
                ),
                ("starts_at", models.TimeField()),
                ("ends_at", models.TimeField()),
                (
                    "relevant_year_groups",
                    models.ManyToManyField(related_name="slots", to="data.yeargroup"),
                ),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data.school"
                    ),
                ),
            ],
            options={
                "ordering": ["day_of_week", "starts_at"],
                "unique_together": {("school", "slot_id")},
            },
        ),
        migrations.CreateModel(
            name="Teacher",
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
                ("teacher_id", models.IntegerField()),
                ("firstname", models.CharField(max_length=20)),
                ("surname", models.CharField(max_length=20)),
                ("title", models.CharField(max_length=10)),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data.school"
                    ),
                ),
            ],
            options={
                "unique_together": {("school", "teacher_id")},
            },
        ),
        migrations.CreateModel(
            name="Pupil",
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
                ("pupil_id", models.IntegerField()),
                ("firstname", models.CharField(max_length=20)),
                ("surname", models.CharField(max_length=20)),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data.school"
                    ),
                ),
                (
                    "year_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pupils",
                        to="data.yeargroup",
                    ),
                ),
            ],
            options={
                "ordering": ["surname", "firstname"],
                "unique_together": {("school", "pupil_id")},
            },
        ),
        migrations.CreateModel(
            name="Profile",
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
                (
                    "role",
                    models.IntegerField(
                        choices=[(1, "Administrator"), (2, "Teacher"), (3, "Pupil")],
                        default=1,
                    ),
                ),
                ("approved_by_school_admin", models.BooleanField(default=False)),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data.school"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Classroom",
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
                ("classroom_id", models.IntegerField()),
                ("building", models.CharField(max_length=20)),
                ("room_number", models.IntegerField()),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data.school"
                    ),
                ),
            ],
            options={
                "unique_together": {
                    ("school", "classroom_id"),
                    ("school", "building", "room_number"),
                },
            },
        ),
        migrations.CreateModel(
            name="Lesson",
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
                ("lesson_id", models.CharField(max_length=20)),
                ("subject_name", models.CharField(max_length=20)),
                ("total_required_slots", models.PositiveSmallIntegerField()),
                ("total_required_double_periods", models.PositiveSmallIntegerField()),
                (
                    "classroom",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lessons",
                        to="data.classroom",
                    ),
                ),
                (
                    "pupils",
                    models.ManyToManyField(related_name="lessons", to="data.pupil"),
                ),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data.school"
                    ),
                ),
                (
                    "solver_defined_time_slots",
                    models.ManyToManyField(
                        related_name="solver_lessons", to="data.timetableslot"
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lessons",
                        to="data.teacher",
                    ),
                ),
                (
                    "user_defined_time_slots",
                    models.ManyToManyField(
                        related_name="user_lessons", to="data.timetableslot"
                    ),
                ),
            ],
            options={
                "unique_together": {("school", "lesson_id")},
            },
        ),
        migrations.CreateModel(
            name="Break",
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
                ("break_id", models.CharField(max_length=20)),
                ("break_name", models.CharField(max_length=20)),
                (
                    "day_of_week",
                    models.SmallIntegerField(
                        choices=[
                            (1, "Monday"),
                            (2, "Tuesday"),
                            (3, "Wednesday"),
                            (4, "Thursday"),
                            (5, "Friday"),
                            (6, "Saturday"),
                            (7, "Sunday"),
                        ]
                    ),
                ),
                ("starts_at", models.TimeField()),
                ("ends_at", models.TimeField()),
                (
                    "relevant_year_groups",
                    models.ManyToManyField(related_name="breaks", to="data.yeargroup"),
                ),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data.school"
                    ),
                ),
                (
                    "teachers",
                    models.ManyToManyField(related_name="breaks", to="data.teacher"),
                ),
            ],
            options={
                "unique_together": {("school", "break_id")},
            },
        ),
    ]
