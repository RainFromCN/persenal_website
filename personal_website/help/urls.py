# URL patterns in polls/urls.py
from django.urls import path
from . import views

app_name = "help"

urlpatterns = [
    path("", views.index, name='index'),
    path("login/", views.login, name='login'),
    path("signup/", views.signup, name='signup'),
    path("exit/", views.exit, name='exit'),
    path("request_publish/", views.request_publish, name='request_publish'),
    path("bidding/<int:request_id>/", views.bidding, name='bidding'),
    path("detail/<int:request_id>/", views.detail, name='detail'),
    path("edit_information/", views.edit_information, name='edit_information'),
    path("cooperation/", views.cooperation, name='cooperation'),
]