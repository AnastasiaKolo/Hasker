import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from django.urls import reverse # Used in get_absolute_url() to get URL for specified ID


class Tag(models.Model):
    tag_text = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter tags for a question (e.g. Linux, DB, Network etc.)")

    def __str__(self):
        return f"{self.tag_text}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower('tag_text'),
                name='tag_text_case_insensitive_unique',
                violation_error_message = "Tag already exists (case insensitive match)"
            ),
        ]


class Question(models.Model):
    title = models.CharField(max_length=200)
    question_text = models.TextField()
    votes = models.IntegerField(default=0)
    # author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField("date created", default=datetime.datetime.now)
    tags = models.ManyToManyField(
        Tag,
        related_name="questions",
        help_text="Select tags for this question")

    def __str__(self):
        return f"{self.id} {self.title}"

    @admin.display(
        boolean=True,
        ordering="created",
        description="Created recently?",
    )
    def was_created_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.created <= now

    class Meta:
        ordering = ['created']
        
    def get_absolute_url(self):
        """Returns the URL to access a particular instance of the model."""
        return reverse('qa:detail', args=[str(self.id)])

    def display_tags(self):
        """Create a string for the Tags. This is required to display tags in Admin."""
        return ', '.join(tag.tag_text for tag in self.tags.all())

    display_tags.short_description = 'Tags'
    
    
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    votes = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    created = models.DateTimeField("date created", default=datetime.datetime.now)
    # author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} ({self.answer_text})"

    class Meta:
        ordering = ['created']
        