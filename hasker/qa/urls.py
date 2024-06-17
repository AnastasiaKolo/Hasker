from django.urls import path

from . import views

app_name = "qa"
urlpatterns = [
    # ex: /qa/
    path("", views.IndexView.as_view(), name="index"),
    # ex: /qa/5/ - detail view question and its answers
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    # ex: /qa/5/answer/ -
    path("<int:question_id>/answer/", views.answer, name="answer"),
]
