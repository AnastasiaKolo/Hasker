""" Forms form where users can update their profile  """

from django.forms import ModelForm, EmailField, CharField, TextInput, ImageField, FileInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profile


class SignUpForm(UserCreationForm):
    """ Add avatar to standard user creation form """
    avatar = ImageField(widget=FileInput(attrs={'class': 'form-control-file'}))
    email = EmailField(required=True)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email", "password1", "password2", "avatar"]


class UserUpdateForm(ModelForm):
    """ Interacts with the user model to let users update their username and email """
    username = CharField(
        max_length=100, 
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}))
    email = EmailField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(ModelForm):
    """ Interacts with the profile model to let users update their avatar """
    avatar = ImageField(widget=FileInput(attrs={'class': 'form-control-file'}))

    class Meta:
        model = Profile
        fields = ["avatar"]
