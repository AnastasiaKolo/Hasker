from django import template
from django.conf import settings

from ..models import Question

register = template.Library()


@register.simple_tag
def top_questions():
    questions = Question.objects.all().order_by('-votes_count')[:settings.TRENDING_COUNT]
    return questions
