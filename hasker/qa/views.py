""" Views for Q&A application """
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import paginator
from django.db.models import F, Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, resolve
from django.views import generic
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, FormView

from .models import Answer, Question, Tag
from .forms import AnswerForm

# https://docs.djangoproject.com/en/5.0/topics/class-based-views/generic-display/
class QuestionListView(generic.ListView):
    """ View for listing all questions or for search results """
    model = Question
    template_name = "qa/question_list.html"
    context_object_name = "questions"
    title = ""
    search_phrase = ""
    tag_text = ""
    paginate_by = settings.PAGINATE_QUESTIONS
    
    
    def dispatch(self, request, *args, **kwargs):
        url_name = resolve(self.request.path).url_name
        if url_name == "tag_detail":
            self.tag_text = self.kwargs.get("name", "")
            self.title = f"Tags: {self.tag_text}"
        
        elif url_name == "search_results":
            self.search_phrase = self.request.GET.get("q", "")
            
            if not self.search_phrase:
                return HttpResponseBadRequest("Empty search phrase")
            self.title = f"Search results: {self.search_phrase}"
            
            if self.search_phrase.startswith("tag:"):
                tag_text = self.search_phrase[4:].strip()
                if not tag_text:
                    return HttpResponseBadRequest("Empty tag")
                return redirect("qa:tag_detail", name=tag_text)
        else:
            self.title = "Latest questions list"
            
        return super().dispatch(request, *args, **kwargs)
    
    
    def get_queryset(self):
        if self.search_phrase:
            questions = Question.objects.filter(
                Q(title__icontains=self.search_phrase) |
                Q(question_text__icontains=self.search_phrase)
            )
        elif self.tag_text:
            tag = get_object_or_404(Tag, tag_text=self.tag_text)
            questions = tag.questions.all()
        else:
            questions = Question.objects.all()

        return questions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["tag"] = self.tag_text
        context["search_phrase"] = self.search_phrase

        num_visits = self.request.session.get('num_visits', 0)
        self.request.session['num_visits'] = num_visits + 1
        context['num_visits'] = num_visits
        
        return context


class QuestionDetailView(generic.DetailView):
    """ Shows question detail with its answers"""
    model = Question
    template_name = "qa/question_detail.html"
    context_object_name = "question"
    answers_paginate_by = settings.PAGINATE_ANSWERS
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AnswerForm()

        answers_page = self.request.GET.get("page", 1)
        
        answers = self.object.answer_set.all()
        answers_paginator = paginator.Paginator(
            answers, self.answers_paginate_by
        )
        
        try:  # Catch invalid page numbers
            answers_page_obj = answers_paginator.page(answers_page)
        except (paginator.PageNotAnInteger, paginator.EmptyPage):
            answers_page_obj = answers_paginator.page(1)

        context["answers_page_obj"] = answers_page_obj
        context["answers"] = answers_page_obj.object_list

        return context

    def post(self, request, *args, **kwargs):
        """ Used for posting answer to the question """
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return super().get(request, *args, **kwargs)

        form = AnswerForm(request.POST)
        if form.is_valid():
            answer_instance = Answer(
                answer_text=form.cleaned_data['answer_text'],
                author=request.user,
                question=self.object
            )
            answer_instance.save()
            form = AnswerForm()

        context = self.get_context_data(object=self.object)
        context["form"] = form
        return self.render_to_response(context)


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


class QuestionCreate(LoginRequiredMixin, CreateView):
    model = Question
    fields = ['title', 'question_text', 'tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
