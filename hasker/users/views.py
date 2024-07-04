from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import UserUpdateForm, ProfileUpdateForm


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = 'Successfully Changed Your Password'
    success_url = reverse_lazy('users:profile')


@login_required
def profile(request):
    """ Create instances of required forms depending on whether the request is get or post """
    # profile_obj = get_object_or_404(Profile, user=request.user)
    # return render(request, "users/profile.html", {"profile": profile_obj})
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
