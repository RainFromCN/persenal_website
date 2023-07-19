from django.urls import path
from . import views


app_name = 'project'


urlpatterns = [
    path("", views.index, name='index'),
    path("signup/", views.signup, name='signup'),
    path("login/", views.login, name='login'),
    path("exit/", views.exit, name='exit'), # 用于退出登录
    path("detail/id=<int:prj_id>/page=<int:page>", views.detail, name='detail'), # 查询详情页面
]