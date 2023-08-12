# URL patterns in polls/urls.py
from django.urls import path
from . import views, chat, share

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
    path("make_cooperation/", views.make_cooperation, name='make_cooperation'),
    path("cooperation/<int:cooperation_id>/", views.cooperation, name="cooperation"),
    path("convert_md_to_html/", views.convert_md_to_html, name='convert_md_to_html'),
    path("submit/request_document/", views.submit_request_document, name='submit_request_document'),
    path("submit/entry_next_step/", views.entry_next_step, name='entry_next_step'),
    path("submit/finish_date/", views.submit_finish_date, name='submit_finish_date'),
    path("submit/fix_finish_date/", views.submit_fix_finish_date, name='submit_fix_finish_date'),
    path("submit/acceptance_date/", views.submit_acceptance_date, name='submit_acceptance_date'),
    path("submit/fix_acceptance_date/", views.submit_fix_acceptance_date, name='submit_fix_acceptance_date'),
    path("get/chat_msgs/", chat.get_chat_msgs, name='get_chat_msgs'),
    path("remove/chat_msgs/", chat.remove_chat_msgs, name='remove_chat_msgs'),
    path("share/<str:room>/", share.share, name='share'),
]
