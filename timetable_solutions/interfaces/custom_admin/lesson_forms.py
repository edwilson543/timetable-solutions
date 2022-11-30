"""
Module containing the add / change form on the LessonModelAdmin
"""

# Django imports
from django import forms

# Local application imports
from data import models


class LessonChangeForm(forms.ModelForm):
    """
    Change form for the Lesson model on the custom admin site.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pupils"].required = False

    class Meta:
        """
        Exclude school / solver_defined_time_slots from the fields since users should not have access to these.
        """
        model = models.Lesson
        fields = ["lesson_id", "subject_name", "total_required_slots", "total_required_double_periods",
                  "teacher", "classroom", "pupils", "user_defined_time_slots"]
