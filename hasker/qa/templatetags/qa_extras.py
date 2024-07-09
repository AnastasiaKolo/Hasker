from django import template
from django.conf import settings

from ..models import Question

register = template.Library()


@register.simple_tag
def top_questions():
    """ Trending questions queryset """
    questions = sorted(Question.objects.all(), key=lambda a: -a.votes_count)[:settings.TRENDING_COUNT]
    return questions
