# Django imports
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views import View
from django.urls import reverse

# Local application imports
from .models import Profile
from .forms import CustomUserCreationForm, SchoolRegistrationPivot, SchoolRegistrationForm, ProfileRegistrationForm
from timetable_selector.models import FixedClass


# Create your views here.
class Register(View):
    """View for step 1 of registering - entering basic details."""
    @staticmethod
    def get(request):
        context = {"form": CustomUserCreationForm}
        return render(request, "users/register.html", context)

    @staticmethod
    def post(request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("registration_pivot"))
        else:
            context = {
                "error_messages": form.error_messages,
                "form": CustomUserCreationForm
            }
            return render(request, "users/register.html", context)


class SchoolRegisterPivot(View):
    """View for step 2 of registering - whether or not school also needs registering"""

    @staticmethod
    def get(request):
        return render(request, "users/register_school_pivot.html", {"form": SchoolRegistrationPivot})

    @staticmethod
    def post(request):
        form = SchoolRegistrationPivot(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("existing_school") == "EXISTING":
                return redirect(reverse("profile_registration"))
            else:
                return redirect(reverse("school_registration"))
        else:
            return redirect(reverse("register"))


class SchoolRegistration(View):
    """View for step 3a of registering - when the school is not registered"""

    @staticmethod
    def get(request):
        return render(request, "users/register_school.html", {"form": SchoolRegistrationForm})

    @staticmethod
    def post(request):
        form = SchoolRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Note this is a model form
            return redirect(reverse("dashboard"))
        else:
            # TODO - create an error message
            pass


class ProfileRegistration(View):
    """View for step 3b of registering - when the school is already registered, just need the access key"""

    @staticmethod
    def get(request):
        return render(request, "users/school_access_key.html", {"form": ProfileRegistrationForm})

    @staticmethod
    def post(request):
        form = ProfileRegistrationForm(request.POST)
        if form.is_valid():
            access_key = form.cleaned_data.get("school_access_key")
            # noinspection PyUnresolvedReferences
            profile = Profile.objects.create(user=request.user, school_id=access_key)
            profile.save()
            return redirect(reverse("dashboard"))
        else:
            # TODO - access key not found message
            pass


def custom_logout(request):
    """
    View redirecting users to the login page when they logout rather than the dashboard, since there is no
    application unless the user is logged in.
    """
    logout(request)
    return redirect(reverse("login"))


def dashboard_view(request):
    """
    Method to add some context to the dashboard view, for rendering in the template.
    This is to restrict the list of options available to users.
    """
    school = request.user.profile.school
    # noinspection PyUnresolvedReferences
    timetable_data_available = FixedClass.objects.filter(school=school)
    context = {"tt_data": timetable_data_available}
    template = loader.get_template("users/dashboard.html")
    return HttpResponse(template.render(context, request))
