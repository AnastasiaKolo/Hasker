from django.urls import path

from . import views

app_name = "qa"
urlpatterns = [
    # ex: /qa/
    path("", views.index, name="index"),
    # ex: /qa/5/ - detail view question and its answers
    path("<int:question_id>/", views.detail, name="detail"),
    # ex: /qa/5/answer/ -
    path("<int:question_id>/answer/", views.answer, name="answer"),
]