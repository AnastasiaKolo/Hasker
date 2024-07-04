""" Users profile model for Q&A application """
from PIL import Image

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User




class Profile(models.Model):
    """ Add some fields to built-in Django user class """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        verbose_name="Profile picture", upload_to="avatars",
        blank=True, null=True
    )
    
    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        """ Resizing images """
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 256 or img.width > 256:
            new_img = (256, 256)
            img.thumbnail(new_img)
            img.save(self.avatar.path)
