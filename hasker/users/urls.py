from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    # ex: /users/5/ - user detail view 
    path("<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
]
