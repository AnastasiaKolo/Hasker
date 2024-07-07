from django.urls import path

from . import views

app_name = "qa"
urlpatterns = [
    # ex: /qa/
    path("", views.QuestionListView.as_view(), name="index"),
    path("search/", views.QuestionListView.as_view(), name="search_results"),
    # ex: /qa/5/ - question_detail view question and its answers
    path("<int:pk>/", views.QuestionDetailView.as_view(), name="question_detail"),
    # ex: /qa/question/create/ - create new question
    path("question/create/", views.QuestionCreate.as_view(), name='question_create'),
    path("tag/<str:name>/", views.QuestionListView.as_view(), name="tag_detail"),
]
