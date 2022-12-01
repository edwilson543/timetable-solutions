"""
Module for the AdminSite instance used to implement the custom AdminSite.
"""

# Django imports
from django import http
from django.contrib import admin
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst

# Local application imports
from data import models


class CustomAdminSite(admin.AdminSite):
    """
    Implementation of the custom AdminSite that users will have access to, to manage their data.
    """

    # Text to put at the end of each page's <title>.
    site_title = "Timetable solutions site admin"

    # Text to put in each page's <h1>.
    site_header = "Timetable solutions administration"

    # Text to put at the top of the admin index page.
    index_title = ""

    def has_permission(self, request: http.HttpRequest) -> bool:
        """
        Users can access the site if their role is 'SCHOOL_ADMIN', which is given to the user registering their
        school for the first time, and this user can give the same privilege to other users.
        """
        if hasattr(request.user, "profile"):
            return request.user.is_active and (request.user.profile.role == models.UserRole.SCHOOL_ADMIN.value)
        else:
            return False

    def _build_app_dict(self, request, label=None):
        """
        Custom override of the base model's method.
        Purpose is to use the CustomModelAdminBase's Meta class' attribute 'custom_app_label', to create custom
        groupings of the models, while maintaining all other properties of the base method (including url conf).
        """
        app_dict = {}

        if label:
            models = {
                m: m_a
                for m, m_a in self._registry.items()
                if m._meta.app_label == label
            }
        else:
            models = self._registry

        for model, model_admin in models.items():
            app_grouping_label = model_admin.Meta.custom_app_label or model._meta.app_label
            app_config_label = model._meta.app_label

            has_module_perms = model_admin.has_module_permission(request)
            if not has_module_perms:
                continue

            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True not in perms.values():
                continue

            info_for_urls = (app_config_label, model._meta.model_name)
            model_dict = {
                "model": model,
                "name": capfirst(model._meta.verbose_name_plural),
                "object_name": model._meta.object_name,
                "perms": perms,
                "admin_url": None,
                "add_url": None,
            }
            if perms.get("change") or perms.get("view"):
                model_dict["view_only"] = not perms.get("change")
                try:
                    model_dict["admin_url"] = reverse(
                        "admin:%s_%s_changelist" % info_for_urls, current_app=self.name
                    )
                except NoReverseMatch:
                    pass
            if perms.get("add"):
                try:
                    model_dict["add_url"] = reverse(
                        "admin:%s_%s_add" % info_for_urls, current_app=self.name
                    )
                except NoReverseMatch:
                    pass

            if app_grouping_label in app_dict:
                app_dict[app_grouping_label]["models"].append(model_dict)
            else:
                app_dict[app_grouping_label] = {
                    "name": app_grouping_label,
                    "app_label": app_grouping_label,
                    "app_url": reverse(
                        "admin:app_list",
                        kwargs={"app_label": app_config_label},
                        current_app=self.name,
                    ),
                    "has_module_perms": has_module_perms,
                    "models": [model_dict],
                }

        return app_dict


# An instance of the CustomAdminSite is created to register all ModelAdmins to
# Note the name given is used to namespace all attached urls when using reverse
user_admin = CustomAdminSite(name="user_admin")
