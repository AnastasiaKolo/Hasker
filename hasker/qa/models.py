from django.contrib.auth.models import User
from django.db import models


class Tag(models.Model):
    tag_text = models.CharField(max_length=200)

    def __str__(self):
        return self.tag_text


class Question(models.Model):
    pub_date = models.DateTimeField("date published")
    title = models.CharField(max_length=200)
    question_text = models.TextField()
    votes = models.IntegerField(default=0)
    # author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField("date created")
    tags = models.ManyToManyField(Tag, related_name="questions")


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    votes = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    created = models.DateTimeField("date created")
    # author = models.ForeignKey(User, on_delete=models.CASCADE)

