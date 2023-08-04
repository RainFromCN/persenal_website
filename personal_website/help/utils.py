from .models import User, Request, RequestFollows, Procedure
from django.http import JsonResponse
from django.db import models
from django.utils import timezone


REQUEST_TYPE = (
    '作业指导',
    '工程外包',
    '科研指导',
)


ALL_FIELDS = (
    '机器视觉',
    '自然语言处理',
    '软件开发',
)


# def _append_delta_time(rqst):
#     delta = timezone.now() - rqst.datetime.astimezone(timezone.utc)
#     delta_days = delta.days
#     delta_seconds = delta.seconds
#     if delta_days > 365:
#         rqst.timedelta = f"{delta_days // 365} 年前发布"
#     elif delta_days > 30:
#         rqst.timedelta = f"{delta_days // 30} 月前发布"
#     elif delta_days > 0:
#         rqst.timedelta = f"{delta_days} 天前发布"
#     elif delta_seconds > 3600:
#         rqst.timedelta = f"{delta_seconds // 3600} 小时前发布"
#     else:
#         rqst.timedelta = "刚刚发布"
#     return rqst


def _get_user_context(request):
    if 'username' in request.session:
        user = User.objects.filter(name=request.session['username']).values().first()
        requests = list(Request.objects.filter(publisher=user).values())
        follows = models.QuerySet([follow.request for follow in RequestFollows.objects.filter(user=user)])
        follows = list(follows.values())
        response = user.update({
            'requests': requests,
            'follows': follows,
        })
        return {'usr': response}
    else:
        return {'usr': None}
    

def _get_other_context():
    return {
        'all_request_type': REQUEST_TYPE,
        'all_fields': ALL_FIELDS,
    },


def _get_all_requests():
    return {'requests': list(Request.objects.all().reverse().values())}


def _get_request_and_follows(r_id):

    # 获取request对象
    request = Request.objects.filter(id=r_id).values().first()

    # 获取该request的所有follows
    follow_list = list(RequestFollows.objects.filter(request=request).order_by('state').reverse().values())
    
    return {
        'request': request,
        'follows': follow_list,
    }


def _get_all_precedures(request):
    if check_login(request) is True:
        res = Procedure.objects.filter(owner__name=request.session['username'])
        return {'procedures': list(res.values())}
    else:
        return {}


def index_data(request):
    my_dict = {}
    my_dict.update(_get_user_context(request))
    my_dict.update(_get_other_context())
    my_dict.update(_get_all_requests())
    return my_dict


def index_detail(request, r_id):
    my_dict = {}
    my_dict.update(_get_request_and_follows(r_id))
    my_dict.update(_get_user_context(request))
    my_dict.update(_get_other_context())
    my_dict.update(_get_all_precedures(request))
    my_dict.update(_get_all_requests())
    return my_dict


def check_login(request):
    return True if 'username' in request.session else False


def logout(request):
    if check_login(request):
        del request.session['username']


def get_user(request):
    return User.objects.get(name=request.session['username'])