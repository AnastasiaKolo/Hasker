""" Forms for Q&A App """
from functools import partial

from django.db import transaction
from django.forms import ModelForm, CharField
from django.conf import settings
from django.core.mail import send_mail
from django.utils.text import Truncator

from .models import Question, Tag, Answer


class AnswerForm(ModelForm):
    """ Add an answer and notify the question author"""

    class Meta:
        """ Class description """
        model = Answer
        fields = ("text",)

    @transaction.atomic
    def save(self, commit=True):
        answer = super().save(commit)
        transaction.on_commit(partial(self.notify_question_author, answer))
        return answer

    @staticmethod
    def notify_question_author(answer):
        """ Notify the author of the question when a new answer is added """
        title_truncated = Truncator(answer.question.title)

        subject = f"New reply for '{title_truncated.words(5)}' - Hasker"
        message = f"""
            <p>{answer.author.username} has replied to your question
            <a href="{answer.question.url}">{title_truncated.words(10)}</a>:</p>
            <p>{Truncator(answer.text).words(25)}</p>
        """
        from_email = settings.TECH_EMAIL
        recipient_list = [answer.question.author.email]

        send_mail(
            subject, message, from_email, recipient_list, fail_silently=True
        )

class TagForm(ModelForm):

    name = CharField(max_length=100)

    class Meta:
        model = Tag
        fields = ("name",)
