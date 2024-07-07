from django import template
from django.conf import settings
from django.db.models import F, Count

from ..models import Question

register = template.Library()


@register.simple_tag
def top_questions():
    questions = Question.objects.all().order_by('-votes')[:settings.PAGINATE_QUESTIONS]
    return questions
