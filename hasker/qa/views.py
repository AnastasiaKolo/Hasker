""" Views for Q&A application """
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import paginator
from django.db.models import F, Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpRequest

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, resolve, reverse_lazy
from django.views import generic
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, FormView

from .models import Answer, Question, Tag
from .forms import AnswerForm, TagForm

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
                text=form.cleaned_data['text'],
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
        current_vote = question.answer_set.get(user=request.user)
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
    fields = ['title', 'text', 'tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BaseVoteView(LoginRequiredMixin, CreateView):

    http_method_names = ["get"]

    def get_redirect_url(self) -> str:

        if issubclass(self.model, Question):
            url_for_redirect = reverse_lazy("qa:index")

        elif issubclass(self.model, Answer):
            answer = get_object_or_404(self.model, id=int(self.kwargs.get(self.pk_url_kwarg)))
            url_for_redirect = reverse_lazy("qa:question", args=(answer.question.id,))

        else:
            raise ValueError(
                f"Wrong model instance. "
                f"Should be one of (Question, Answer), not {type(self.model)}"
            )

        return url_for_redirect

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        action_object_id = int(self.kwargs.get(self.pk_url_kwarg))
        action_object = get_object_or_404(self.model, id=action_object_id)
        action_object.make_user_action(
            user=self.request.user,
            action=int(self.kwargs.get("action"))
        )

        return HttpResponseRedirect(self.get_redirect_url())


class QuestionVoteView(BaseVoteView):

    model = Question
    pk_url_kwarg = "question_id"


class AnswerVoteView(BaseVoteView):

    model = Answer
    pk_url_kwarg = "answer_id"

class MarkCorrectAnswerView(LoginRequiredMixin, generic.RedirectView):

    pattern_name = "qa:question"

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy(self.pattern_name, kwargs={"question_id": kwargs["question_id"]})

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        question = get_object_or_404(Question, id=kwargs["question_id"])
        answer = get_object_or_404(Answer, id=kwargs["answer_id"])
        question.correct_answer = answer
        question.save()

        return super().get(request, *args, **kwargs)


class CreateTagView(LoginRequiredMixin, CreateView):

    object: Tag
    form_class = TagForm
    template_name = "qa/create_tag.html"
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("qa:index")
