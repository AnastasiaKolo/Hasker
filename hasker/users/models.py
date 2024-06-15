from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    registered = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(
        verbose_name="Profile picture", upload_to="avatars",
        blank=True, null=True
    )

    @property
    def url(self):
        return reverse('user:profile', kwargs={'username': self.username})
