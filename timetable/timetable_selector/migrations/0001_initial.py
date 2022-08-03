# Generated by Django 4.0.6 on 2022-08-03 06:28

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pupil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=20)),
                ('surname', models.CharField(max_length=20)),
                ('year_group', models.IntegerField(choices=[(1, '#b3f2b3'), (2, '#ffbfd6'), (3, '#c8d4e3'), (4, '#fcc4a2'), (5, '#babac2')])),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=20)),
                ('surname', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TimetableSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(choices=[('MONDAY', 'Monday'), ('TUESDAY', 'Tuesday'), ('WEDNESDAY', 'Wednesday'), ('THURSDAY', 'Thursday'), ('FRIDAY', 'Friday')], max_length=9)),
                ('period_start_time', models.TimeField(choices=[(datetime.time(9, 0), 'PERIOD_ONE'), (datetime.time(10, 0), 'PERIOD_TWO'), (datetime.time(11, 0), 'PERIOD_THREE'), (datetime.time(12, 0), 'PERIOD_FOUR'), (datetime.time(13, 0), 'LUNCH'), (datetime.time(14, 0), 'PERIOD_FIVE'), (datetime.time(15, 0), 'PERIOD_SIX')])),
                ('period_duration', models.DurationField(default=datetime.timedelta(seconds=3600))),
            ],
        ),
        migrations.CreateModel(
            name='FixedClass',
            fields=[
                ('class_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('subject_name', models.CharField(choices=[('#b3f2b3', 'Maths'), ('#ffbfd6', 'English'), ('#c8d4e3', 'French'), ('#b3b3b3', 'Lunch'), ('#feffba', 'Free')], max_length=20)),
                ('pupils', models.ManyToManyField(related_name='classes', to='timetable_selector.pupil')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='classes', to='timetable_selector.teacher')),
                ('time_slots', models.ManyToManyField(related_name='classes', to='timetable_selector.timetableslot')),
            ],
        ),
    ]
