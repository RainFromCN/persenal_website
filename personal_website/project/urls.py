from django.urls import path
from . import views


app_name = 'project'


urlpatterns = [
    path("", views.index, name='index'),
    path("signup/", views.signup, name='signup'),
    path("login/", views.login, name='login'),
    path("exit/", views.exit, name='exit'), # 用于退出登录
    path("detail/id=<int:prj_id>/page=<int:page>", views.detail, name='detail'), # 查询详情页面
    path("detail/id=<int:prj_id>/<str:filename>", views.image, name='image'), # 查询图片页面
    path("activate/id=<int:prj_id>", views.activate, name='activate'), # 激活页面
    path("tutorial/id=<int:prj_id>/chapter=<int:chapter_id>", views.tutorial, name='tutorial'), # 教程页面
]