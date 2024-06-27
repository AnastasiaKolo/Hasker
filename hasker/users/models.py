""" Users profile model for Q&A application """

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
#from django.contrib.auth.models import AbstractUser

class Profile(models.Model):
    """ Add some fields to built-in Django user class """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        verbose_name="Profile picture", upload_to="avatars",
        blank=True, null=True
    )

    def get_absolute_url(self):
        """ Get url to the profile """
        return reverse('user:profile', kwargs={'username': self.user.username})

    @property
    def url(self):
        """ Get url to the profile as property """
        return self.get_absolute_url()
