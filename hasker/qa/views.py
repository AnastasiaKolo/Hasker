""" Views for Q&A application """
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import paginator
from django.core.mail import send_mail

from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpRequest

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, resolve, reverse_lazy
from django.utils.text import Truncator
from django.views.generic import ListView, DetailView, RedirectView
from django.views.generic.edit import CreateView

from .models import Answer, Question, Tag
from .forms import AnswerForm, TagForm, QuestionForm

# https://docs.djangoproject.com/en/5.0/topics/class-based-views/generic-display/
class QuestionListView(ListView):
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
            self.tag_text = self.kwargs.get("tag_text", "")
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
                return redirect("qa:tag_detail", tag_text=tag_text)
        else:
            self.title = "Latest questions list"
            
        return super().dispatch(request, *args, **kwargs)
    
    
    def get_queryset(self):
        if self.search_phrase:
            questions = Question.objects.filter(
                Q(title__icontains=self.search_phrase) |
                Q(text__icontains=self.search_phrase)
            )
        elif self.tag_text:
            tag = get_object_or_404(Tag, tag_text=self.tag_text)
            questions = tag.questions.all()
        else:
            questions = Question.objects.all()
        questions = questions.annotate(num_answers=Count("answer"))

        return sorted(questions, key=lambda a: (a.votes_count, a.created), reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["tag"] = self.tag_text
        context["search_phrase"] = self.search_phrase

        num_visits = self.request.session.get('num_visits', 0)
        self.request.session['num_visits'] = num_visits + 1
        context['num_visits'] = num_visits

        return context


class TagListView(ListView):
    model = Tag
    paginate_by = 100


class QuestionDetailView(DetailView):
    """ Shows question detail with its answers"""
    model = Question
    template_name = "qa/question_detail.html"
    context_object_name = "question"
    answers_paginate_by = settings.PAGINATE_ANSWERS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AnswerForm()

        answers_page = self.request.GET.get("page", 1)

        answers = sorted(
            self.object.answer_set.all(), 
            key=lambda a: (a.votes_count, a.created), reverse=True)

        context["answers"] = answers
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
        print('posting answer')
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
            self.notify_question_author(answer_instance)
            form = AnswerForm()

        context = self.get_context_data(object=self.object)
        context["form"] = form

        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("qa:question_detail", args=(self.object.id,)))

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
        print(f'sending mail to {recipient_list}' )
        send_mail(
            subject, message, from_email, recipient_list
        )


class QuestionCreate(LoginRequiredMixin, CreateView):
    """ Create question """
    model = Question
    form_class = QuestionForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class TagCreate(LoginRequiredMixin, CreateView):
    """ Create new tag """
    model = Tag
    form_class = TagForm
    success_url = reverse_lazy("qa:tag_list")


class BaseVoteView(LoginRequiredMixin, CreateView):
    """ Base view for voting for questions or answers """
    http_method_names = ["get"]

    def get_redirect_url(self, request: HttpRequest) -> str:
        """ Get the page to go to after voting """
        if issubclass(self.model, Question):
            # redirect to parameter next if exists
            url_for_redirect = request.GET.get('next', reverse_lazy("qa:index"))

        elif issubclass(self.model, Answer):
            answer = get_object_or_404(Answer, id=int(self.kwargs.get(self.pk_url_kwarg)))
            url_for_redirect = reverse_lazy("qa:question_detail", args=(answer.question.id,))

        else:
            raise ValueError(
                f"Wrong model instance. "
                f"Should be one of (Question, Answer), not {type(self.model)}"
            )

        return url_for_redirect

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """ Vote for question or answer """
        action_object_id = int(self.kwargs.get(self.pk_url_kwarg))
        action_object = get_object_or_404(self.model, id=action_object_id)
        action_object.do_vote(
            user=self.request.user,
            current_vote=int(self.kwargs.get("vote"))
        )

        return HttpResponseRedirect(self.get_redirect_url(request))


class QuestionVoteView(BaseVoteView):

    model = Question
    pk_url_kwarg = "question_id"


class AnswerVoteView(BaseVoteView):

    model = Answer
    pk_url_kwarg = "answer_id"


class MarkCorrectAnswerView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("qa:question_detail", args=[kwargs["question_id"]])

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        question = get_object_or_404(Question, id=kwargs["question_id"])
        answer = get_object_or_404(Answer, id=kwargs["answer_id"])
        question.correct_answer = answer
        question.save()

        return super().get(request, *args, **kwargs)
