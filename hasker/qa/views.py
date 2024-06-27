""" Views for Q&A application """

from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Answer, Question, Tag


# https://docs.djangoproject.com/en/5.0/topics/class-based-views/generic-display/
class IndexView(generic.ListView):
    model = Question
    template_name = "qa/index.html"
    context_object_name = "latest_question_list"
    paginate_by = 20
    
    # def get_queryset(self):
    #     """Return the last 20 created questions."""
    #     return Question.objects.order_by("-created")[:20]
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Generate counts of some of the main objects
        context['num_questions'] = Question.objects.count()
        context['num_answers'] = Answer.objects.count()
        context['num_tags'] = Tag.objects.count()

        #TODO
        context['num_users'] = 0
        
        num_visits = self.request.session.get('num_visits', 0)
        self.request.session['num_visits'] = num_visits + 1
        context['num_visits'] = num_visits
        
        return context
    
    

class QuestionDetailView(generic.DetailView):
    model = Question
    template_name = "qa/question_detail.html"


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
            "qa/question_detail.html",
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
# def question_detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "qa/question_detail.html", {"question": question})


def answer(request, question_id):
    return HttpResponse("You're answering to question %s." % question_id)


# def index(request):
#     latest_question_list = Question.objects.order_by("-created")[:5]
#     context = {"latest_question_list": latest_question_list}
#     return render(request, "qa/index.html", context)
