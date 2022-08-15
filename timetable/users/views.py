from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.urls import reverse
from django.views import View


# Create your views here.
class Register(View):

    @staticmethod
    def get(request):
        return render(
            request, "users/register.html",
            {"form": CustomUserCreationForm}
        )

    @staticmethod
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("dashboard"))