"""Views for the teacher data management functionality."""

from typing import Any

from django.contrib.auth import mixins
from django.views import generic


class TeacherLanding(mixins.LoginRequiredMixin, generic.TemplateView):
    """Page users arrive at from 'data/teachers' on the navbar."""

    template_name = "data_management/teachers/landing-page.html"
    http_method_names = ["get"]

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Add some restrictive context for the template."""
        context = super().get_context_data(**kwargs)
        school = self.request.user.profile.school
        context["has_existing_data"] = school.has_teacher_data
        return context
