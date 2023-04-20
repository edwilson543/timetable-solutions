"""
The user dashboard, which *might* at some point get some context.
"""

# Django imports
from django.contrib.auth import mixins
from django.views import generic


class Dashboard(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = "users/dashboard.html"
