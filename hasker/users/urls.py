from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    # ex: /users/profile - current user profile view or edit
    path("profile", views.profile, name="profile"),
    path("password-change/", views.ChangePasswordView.as_view(), name='password_change'),
]
