# Generated by Django 4.1.2 on 2022-11-25 07:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_squashed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lesson_id', models.CharField(max_length=20)),
                ('subject_name', models.CharField(max_length=20)),
                ('total_required_slots', models.PositiveSmallIntegerField()),
                ('total_required_double_periods', models.PositiveSmallIntegerField()),
                ('classroom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lessons', to='data.classroom')),
                ('pupils', models.ManyToManyField(related_name='lessons', to='data.pupil')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.school')),
                ('solver_defined_time_slots', models.ManyToManyField(related_name='solver_classes', to='data.timetableslot')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lessons', to='data.teacher')),
                ('user_defined_time_slots', models.ManyToManyField(related_name='user_classes', to='data.timetableslot')),
            ],
            options={
                'unique_together': {('school', 'lesson_id')},
            },
        ),
    ]
