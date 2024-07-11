""" Views for managing user profiles """
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import UserUpdateForm, ProfileUpdateForm, SignUpForm
from .models import User, Profile


def signup(request):
    """ Function-based view for SignUp form """
    if request.method == "POST":
        print(request.POST, request.FILES)
        user_form = SignUpForm(request.POST, request.FILES)
        if user_form.is_valid():
            user_form.save()
            avatar = user_form.cleaned_data.get('avatar')
            username = user_form.cleaned_data.get('username')
            user = User.objects.get(username=username)
            user_profile = Profile.objects.get_or_create(user=user)[0]
            user_profile.avatar = avatar
            user_profile.save()
            return redirect(to="login")
    else:
        user_form = SignUpForm()

    return render(
        request,
        'registration/signup.html',
        {'user_form': user_form})


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = 'Successfully Changed Your Password'
    success_url = reverse_lazy('users:profile')


@login_required
def profile(request):
    """ Create instances of required forms depending on whether the request is get or post """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(
        request,
        'users/profile.html',
        {'user_form': user_form, 'profile_form': profile_form})
