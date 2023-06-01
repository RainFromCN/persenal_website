from django.urls import path
from . import views


app_name = 'project'


urlpatterns = [
    path("", views.index, name='index'),
    path("<int:prj_id>/introduction/", views.introduction, name='introduction'),
    path("<int:prj_id>/paper/", views.paper, name='paper'),
    path("<int:prj_id>/tutorial/", views.tutorial, name='tutorial'),
    path("<int:prj_id>/image/<str:filename>", views.image, name='image'),
]