# URL patterns in polls/urls.py
from django.urls import path
from . import views, chat, share, buy, backend

app_name = "help"

urlpatterns = [
    path("", views.index, name='index'),
    path("login/", views.login, name='login'),
    path("signup/", views.signup, name='signup'),
    path("exit/", views.exit, name='exit'),
    path("backend/", backend.backend, name="backend"),
    path("request_publish/", views.request_publish, name='request_publish'),
    path("bidding/<int:request_id>/", views.bidding, name='bidding'),
    path("detail/<int:request_id>/", views.detail, name='detail'),
    path("edit_information/", views.edit_information, name='edit_information'),
    path("make_cooperation/", views.make_cooperation, name='make_cooperation'),
    path("cooperation/<int:cooperation_id>/", views.cooperation, name="cooperation"),
    path("convert_md_to_html/", views.convert_md_to_html, name='convert_md_to_html'),
    path("submit/request_document/", views.submit_request_document, name='submit_request_document'),
    path("submit/entry_next_step/", views.entry_next_step, name='entry_next_step'),
    path("submit/cancel_cooperation/", views.submit_cancel_cooperation, name='submit_cancel_cooperation'),
    path("submit/rate_and_review/", views.submit_rate_and_review, name='submit_rate_and_review'),
    path("submit/appeal/", views.submit_appeal, name="submit_appeal"),
    path("get/chat_msgs/", chat.get_chat_msgs, name='get_chat_msgs'),
    path("get/deposit_pay_link/", buy.get_deposit_pay_link, name="get_deposit_pay_link"),
    path("get/pay_link/", buy.get_pay_link, name="get_pay_link"),
    path("remove/chat_msgs/", chat.remove_chat_msgs, name='remove_chat_msgs'),
    path("remove/appeal/", views.remove_appeal, name="remove_appeal"),
    path("share/<str:room>/", share.share, name='share'),
    path("check/deposit/", buy.check_deposit),
    path("check/transfer/", buy.check_transfer),
    path("check/payment/", buy.check_payment),
    path("refund/deposit/", buy.refund_deposit),
    path("submit/appeal_result/", views.submit_appeal_result),
    path("transfer_payment/", buy.transfer_payment),
]
