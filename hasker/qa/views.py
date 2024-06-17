
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404

from .models import Question


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "qa/detail.html", {"question": question})


def answer(request, question_id):
    return HttpResponse("You're answering to question %s." % question_id)


def index(request):
    latest_question_list = Question.objects.order_by("-created")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "qa/index.html", context)
