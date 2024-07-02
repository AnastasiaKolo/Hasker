from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import Profile

# Create your views here.
class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = Profile
    template_name = "users/profile.html"
