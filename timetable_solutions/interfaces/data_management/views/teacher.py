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


class TeacherSearchList(base_views.SearchListBase):
    """Page displaying all a school's teacher data and allowing them to search for teachers."""

    # Django vars
    template_name = "data_management/teacher/teacher-list.html"
    form_class = forms.TeacherSearch

    # Custom vars
    model = models.Teacher
    search_help_text = "Search for a teacher by name or id."
    form_post_url = UrlName.TEACHER_LIST.url(lazy=True)

    def execute_search_from_clean_form(
        self, form: forms.TeacherSearch
    ) -> models.TeacherQuerySet:
        """Get the queryset of teachers matching the search term."""
        search_term = form.cleaned_data["search_term"]
        return teacher_queries.get_teachers_by_search_term(
            school_id=self.school_id, search_term=search_term
        )
