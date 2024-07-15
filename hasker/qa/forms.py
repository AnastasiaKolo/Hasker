""" Forms for Q&A App """
from django.forms import (ModelForm, CharField, ModelMultipleChoiceField, SelectMultiple, ValidationError)

from .models import Question, Tag, Answer


class AnswerForm(ModelForm):
    """ Add an answer """
    class Meta:
        """ Class description """
        model = Answer
        fields = ("text",)


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
