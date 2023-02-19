"""Views for the teacher data management functionality."""

from typing import Any

from django.contrib.auth import mixins
from django.views import generic

from data import models
from domain.data_management.teachers import queries as teacher_queries
from interfaces.data_management.views import base_views
from interfaces.data_management import forms
from interfaces.constants import UrlName


class TeacherLanding(mixins.LoginRequiredMixin, generic.TemplateView):
    """Page users arrive at from 'data/teachers' on the navbar."""

    template_name = "data_management/teacher/landing-page.html"
    http_method_names = ["get"]

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Add some restrictive context for the template."""
        context = super().get_context_data(**kwargs)
        school = self.request.user.profile.school
        context["has_existing_data"] = school.has_teacher_data
        return context


class TeacherSearch(base_views.SearchView):
    """Page displaying all a school's teacher data and allowing them to search for teachers."""

    # Django vars
    template_name = "data_management/teacher/teacher-list.html"
    ordering = ["teacher_id"]

    # Generic class vars
    model_class = models.Teacher
    form_class = forms.TeacherSearch

    # Ordinary class vars
    displayed_fields = {
        "teacher_id": "Teacher ID",
        "firstname": "Firstname",
        "surname": "Surname",
    }
    search_help_text = "Search for a teacher by name or id."
    page_url = UrlName.TEACHER_LIST.url(lazy=True)

    def execute_search_from_clean_form(
        self, form: forms.TeacherSearch
    ) -> models.TeacherQuerySet:
        """Get the queryset of teachers matching the search term."""
        search_term = form.cleaned_data["search_term"]
        return teacher_queries.get_teachers_by_search_term(
            school_id=self.school_id, search_term=search_term
        )


class TeacherUpdate(base_views.UpdateView):
    """
    Page displaying information on a single teacher, and allowing this data to be updated.
    """

    # Django vars
    template_name = "data_management/teacher/teacher-detail-update.html"

    # Generic class vars
    form_class = forms.TeacherUpdate
    model_class = models.Teacher

    # Ordinary class vars
    object_id_name = "teacher_id"
    model_attributes_for_form_initials = ["firstname", "surname", "title"]
    page_url_prefix = UrlName.TEACHER_UPDATE
