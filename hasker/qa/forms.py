""" Forms for Q&A App """
from functools import partial

from django.db import transaction
from django.forms import (ModelForm, CharField, ModelMultipleChoiceField, SelectMultiple, ValidationError)
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
    """ Tag creation form """
    tag_text = CharField(max_length=100)

    class Meta:
        model = Tag
        fields = ("tag_text",)


class QuestionForm(ModelForm):
    tags = ModelMultipleChoiceField(
        required=False,
        to_field_name="tag_text",
        queryset=Tag.objects.all(),
        widget=SelectMultiple(attrs={'class': 'multiselect'})
    )

    class Meta:
        model = Question
        fields = ("title", "text", "tags", )

    def clean_tags(self):
        tags = self.cleaned_data["tags"]
        if len(tags) > 3:
            raise ValidationError(
                "You can choose 3 tags maximum",
                code="exceeding_tags_limit"
            )
        return tags
