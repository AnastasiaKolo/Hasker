from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Answer, Question


class IndexView(generic.ListView):
    template_name = "qa/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        # return Question.objects.order_by("-created")[:5]
        return Question.objects.filter(created__lte=timezone.now()).order_by("-created")[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = "qa/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(created__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "qa/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_answer = question.answer_set.get(pk=request.POST["choice"])
    except (KeyError, Answer.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "qa/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_answer.votes = F("votes") + 1
        selected_answer.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("qa:results", args=(question.id,)))

# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "qa/results.html", {"question": question})
#
#
# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "qa/detail.html", {"question": question})


def answer(request, question_id):
    return HttpResponse("You're answering to question %s." % question_id)


# def index(request):
#     latest_question_list = Question.objects.order_by("-created")[:5]
#     context = {"latest_question_list": latest_question_list}
#     return render(request, "qa/index.html", context)
