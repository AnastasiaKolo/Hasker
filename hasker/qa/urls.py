from django.urls import path

from . import views

app_name = "qa"
urlpatterns = [
    # ex: /qa/
    path("", views.IndexView.as_view(), name="index"),
    # path("", views.index, name="index"),
    # ex: /qa/5/ - question_detail view question and its answers
    path("<int:pk>/", views.QuestionDetailView.as_view(), name="question_detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    # ex: /qa/5/answer/ -
    path("<int:question_id>/answer/", views.answer, name="answer"),
]
