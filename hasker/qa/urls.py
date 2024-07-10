from django.urls import path, re_path

from . import views

app_name = "qa"
urlpatterns = [
    # ex: /qa/
    path("", views.QuestionListView.as_view(), name="index"),
    path("search/", views.QuestionListView.as_view(), name="search_results"),
    # ex: /qa/5/ - question_detail view question and its answers
    path("question/<int:pk>/", views.QuestionDetailView.as_view(), name="question_detail"),
    # ex: /qa/question/create/ - create new question
    path("question/create/", views.QuestionCreate.as_view(), name='question_create'),
    # ex: /qa/tag/create/ - create new tag
    path("tag/create/", views.TagCreate.as_view(), name='tag_create'),
    # ex: /qa/tag/list/ - list all tags
    path("tag/list/", views.TagListView.as_view(), name='tag_list'),
    # ex: /qa/tag/linux - display all questions with this tag
    path("tag/<str:name>/", views.QuestionListView.as_view(), name="tag_detail"),
    # "mark answer as correct" button
    path("question/<int:question_id>/mark_answer_as_correct/<int:answer_id>",
        views.MarkCorrectAnswerView.as_view(),
        name="mark_answer_as_correct"),
    re_path(r'^question/(?P<question_id>\d+)/vote/(?P<vote>[+-]1)',
        views.QuestionVoteView.as_view(),
        name="question_vote"),
    re_path(r'^answer/(?P<answer_id>\d+)/vote/(?P<vote>[+-]1)',
        views.AnswerVoteView.as_view(),
        name="answer_vote")
]
