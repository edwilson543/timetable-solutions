# Generated by Django 4.1.2 on 2022-11-22 08:55

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('data', '0001_initial'), ('data', '0002_profile_role')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('school_access_key', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('school_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacher_id', models.IntegerField()),
                ('firstname', models.CharField(max_length=20)),
                ('surname', models.CharField(max_length=20)),
                ('title', models.CharField(max_length=10)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.school')),
            ],
            options={
                'unique_together': {('school', 'teacher_id')},
            },
        ),
        migrations.CreateModel(
            name='TimetableSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot_id', models.IntegerField()),
                ('day_of_week', models.SmallIntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday')])),
                ('period_starts_at', models.TimeField()),
                ('period_duration', models.DurationField(default=datetime.timedelta(seconds=3600))),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.school')),
            ],
            options={
                'ordering': ['day_of_week', 'period_starts_at'],
                'unique_together': {('school', 'slot_id')},
            },
        ),
        migrations.CreateModel(
            name='Pupil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pupil_id', models.IntegerField()),
                ('firstname', models.CharField(max_length=20)),
                ('surname', models.CharField(max_length=20)),
                ('year_group', models.IntegerField(choices=[(1, 'One'), (2, 'Two'), (3, 'Three'), (4, 'Four'), (5, 'Five'), (6, 'Six'), (7, 'Seven'), (8, 'Eight'), (9, 'Nine'), (10, 'Ten')])),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.school')),
            ],
            options={
                'unique_together': {('school', 'pupil_id')},
            },
        ),
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classroom_id', models.IntegerField()),
                ('building', models.CharField(max_length=20)),
                ('room_number', models.IntegerField()),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.school')),
            ],
            options={
                'unique_together': {('school', 'classroom_id'), ('school', 'building', 'room_number')},
            },
        ),
        migrations.CreateModel(
            name='UnsolvedClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_id', models.CharField(max_length=20)),
                ('subject_name', models.CharField(max_length=20)),
                ('total_slots', models.PositiveSmallIntegerField()),
                ('n_double_periods', models.PositiveSmallIntegerField()),
                ('classroom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='unsolved_classes', to='data.classroom')),
                ('pupils', models.ManyToManyField(related_name='unsolved_classes', to='data.pupil')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.school')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='unsolved_classes', to='data.teacher')),
            ],
            options={
                'unique_together': {('school', 'class_id')},
            },
        ),
        migrations.CreateModel(
            name='FixedClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_id', models.CharField(max_length=20)),
                ('subject_name', models.CharField(max_length=20)),
                ('user_defined', models.BooleanField()),
                ('classroom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='classes', to='data.classroom')),
                ('pupils', models.ManyToManyField(related_name='classes', to='data.pupil')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.school')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='classes', to='data.teacher')),
                ('time_slots', models.ManyToManyField(related_name='classes', to='data.timetableslot')),
            ],
            options={
                'unique_together': {('school', 'class_id', 'user_defined')},
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.school')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('role', models.IntegerField(choices=[(1, 'Administrator'), (2, 'Teacher'), (3, 'Pupil')], default=1)),
            ],
        ),
    ]
