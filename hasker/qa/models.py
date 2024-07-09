""" Models for Q&A application """
import datetime 
from typing import Union

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone

from django.urls import reverse


class VoteStatus(models.IntegerChoices):
    """ Status choices for question or answer votes """
    LIKE = 1
    DISLIKE = -1


class Tag(models.Model):
    """ Tags for questions """
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
        ordering = ["tag_text"]


    def get_absolute_url(self):
        """Returns the URL to access a particular instance of the model."""
        return reverse('qa:tag_detail', args=[str(self.tag_text)])


class AbstractQA(models.Model):
    """ Abstract parent for Question and Answer models """

    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField("date created", default=timezone.now)

    class Meta:
        abstract = True

    @transaction.atomic
    def do_vote(self, user: User, current_vote: VoteStatus) -> None:
        """ Like or Dislike vote """
        do_vote(vote_object=self, user=user, current_vote=current_vote)

    @property
    def votes_count(self):
        """ Get total votes count """
        votes = self.votes.aggregate(sum_votes=models.Sum("vote"))["sum_votes"]
        return votes or 0


class Question(AbstractQA):
    """ A question asked by site user """
    title = models.CharField(max_length=200)
    tags = models.ManyToManyField(
        Tag,
        related_name="questions",
        help_text="Select tags for this question")
    correct_answer = models.OneToOneField(
        to="Answer",
        null=True,
        blank=True,
        related_name="correct_answer_for",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.title}"

    @admin.display(
        boolean=True,
        ordering="created",
        description="Created recently?",
    )
    def was_created_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.created <= now

    def get_absolute_url(self):
        """Returns the URL to access a particular instance of the model."""
        return reverse('qa:question_detail', args=[str(self.id)])

    def display_tags(self):
        """Create a string for the Tags. This is required to display tags in Admin."""
        return ', '.join(tag.tag_text for tag in self.tags.all())

    display_tags.short_description = 'Tags'


class Answer(AbstractQA):
    """ An answer to a question """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.text}"


class AbstractVote(models.Model):
    """ Parent class for Question and Answer votes """
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    vote = models.IntegerField(
        choices=VoteStatus.choices,
        blank=True,
        default=0,
        help_text="Vote status")

    def __str__(self):
        return f"{self.vote}"

    class Meta:
        abstract = True


class QuestionVote(AbstractVote):
    """ 
    A User can 'like' or 'dislike' a question 
    Only one vote for one user for each question is available
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="votes",)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "question"],
                name="question_vote_only_one_by_user",
                violation_error_message = "A user can vote for a question only once"
            ),
        ]


class AnswerVote(AbstractVote):
    """ 
    A User can 'like' or 'dislike' an answer 
    Only one vote for one user for each answer is available
    """
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="votes",)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "answer"],
                name="answer_vote_only_one_by_user",
                violation_error_message = "A user can vote for an answer only once"
            ),
        ]


def do_vote(
    vote_object: Union[Question, Answer],
    user: User,
    current_vote: VoteStatus) -> None:

    """
    Vote (like or dislike) for question or answer
    :param vote_object: object to vote for (concrete question or answer)
    :param user: user who votes
    :param status: vote that should be made (like or dislike)
    """

    opposite_vote = VoteStatus.DISLIKE if current_vote == VoteStatus.LIKE else VoteStatus.LIKE
    vote_object.votes.filter(
        models.Q(user_id=user.id) &
        models.Q(vote=opposite_vote)
    ).delete()

    user_action_is_already_done = vote_object.votes.filter(
        models.Q(user_id=user.id) &
        models.Q(vote=current_vote)
    )

    # revoke current vote if the same button is pressed again
    if user_action_is_already_done.exists():
        user_action_is_already_done.delete()
        return

    vote_object.votes.create(
        user_id=user.id,
        vote=current_vote
    )
