import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Tag(models.Model):
    tag_text = models.CharField(max_length=200)

    def __str__(self):
        return self.tag_text


class Question(models.Model):
    title = models.CharField(max_length=200)
    question_text = models.TextField()
    votes = models.IntegerField(default=0)
    # author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField("date created")
    tags = models.ManyToManyField(Tag, related_name="questions")

    def __str__(self):
        return self.title

    @admin.display(
        boolean=True,
        ordering="created",
        description="Created recently?",
    )
    def was_created_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.created <= now


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    votes = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    created = models.DateTimeField("date created")
    # author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.answer_text
