from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from project.models import User, ALL_FIELDS
from .models import Request, REQUEST_TYPE, RequestFollows, Procedure, ProcedureStep


from .utils import (
    check_login, 
    index_data, 
    logout, 
    get_user,
    index_detail,
)


# Create your views here.
@csrf_exempt
def index(request):
    return render(request, "help/index.html", index_data(request))


@csrf_exempt
def detail(request, r_id):
    return render(request, "help/detail.html", index_detail(request, r_id))


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('signup_username')
        password = request.POST.get('signup_password')
        confirm = request.POST.get('signup_confirm')

        cond1 = len(username) == 0 or len(password) == 0
        cond2 = User.objects.filter(name=username).count() > 0
        cond3 = password != confirm

        if cond1:
            return JsonResponse({'message': '用户名或密码的长度必须大于0'})
        elif cond2:
            return JsonResponse({'message': '用户名重复'})
        elif cond3:
            return JsonResponse({'message': '两次输入的密码不一致'})
        else:
            kwargs = {'name': username, 'password': password}
            if introduction := request.POST.get('signup_introduction'):
                kwargs['introduction'] = introduction
            if field := request.POST.get('field'):
                kwargs['field'] = field
            user = User(**kwargs)
            user.save()
            request.session['username'] = username
            return JsonResponse({'success': True})
        

@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get('login_username')
        password = request.POST.get('login_password')

        user = User.objects.filter(name=username).first()

        if not user:
            return JsonResponse({'message': '用户名不存在'})
        elif user.password != password:
            return JsonResponse({'message': '密码错误'})
        else:
            request.session['username'] = username
            return JsonResponse({'success': True})


@csrf_exempt
def exit(request):
    logout(request)
    return JsonResponse({'success': True})


@csrf_exempt
def request_publish(request):

    # 获取发布的用户
    if check_login(request) is False:
        return JsonResponse({'message': '请先登录'})
    user = get_user(request)

    # 创建新的需求信息
    rqst = Request(
        publisher=user, 
        title=request.POST.get('title'),
        content=request.POST.get('detail'),
        field=request.POST.get('field'),
        type=request.POST.get('type'),
    )
    rqst.save()
    
    # 保存用户的相关信息
    user.pub_times += 1
    user.save()

    return JsonResponse({'success': True})


@csrf_exempt
def bidding(request, r_id):
    # 获取投标用户和带投标的需求
    if check_login(request) is False:
        return JsonResponse({'message': '请先登录'})
    user = get_user(request)
    rqst = Request.objects.get(id=r_id)

    # 检查是否合法
    if user.tel == '' or user.introduction == '':
        return JsonResponse({'message': '请先完善个人资料'})
    
    # 从前端获取数据
    bid_price = int(request.POST.get('bid'))
    notify = bool(request.POST.get('notify_new_bids'))

    # 创建投标信息
    follow = RequestFollows(request=rqst, user=user, bid_price=bid_price,
                            notify_new_bids=notify)
    follow.save()

    # 更改投标用户的状态
    user.bid_times += 1
    user.save()

    # 更改需求信息
    if rqst.lowest_bid == '-' or bid_price < int(rqst.lowest_bid):
        rqst.lowest_bid = f'{bid_price}'
        rqst.num_bid += 1
        rqst.save()

    return JsonResponse({'success': True})


@csrf_exempt
def edit_information(request):

    # 检查用户是否已经登录
    if check_login(request) is False:
        return JsonResponse({'message': '请先登录'})
    user = get_user(request)
    
    # 从前端获取数据
    tel = request.POST.get('tel')
    intro = request.POST.get('introduction')

    # 给数据库添加新的项
    user.tel = tel
    user.introduction = intro
    user.save()

    return JsonResponse({'success': True})


@csrf_exempt
def cooperation(request):
    # 获取follow
    follow_id = request.POST.get('id')
    follow = RequestFollows.objects.get(id=follow_id)
    follow.state = 1
    follow.save()

    # 更改状态
    follow.request.state = 1
    follow.user.win_times += 1
    follow.request.save()
    follow.user.save()

    return JsonResponse({"success": True})


@csrf_exempt
def create_procedures(request):
    if check_login(request) is False:
        return JsonResponse({'message': '请先登录后再进行操作'})
    
    # 创建一个流程
    procedure = Procedure(owner=User.objects.filter(name=request.session['username']).first())

    # 给这个流程内添加步骤
    sum_pay = 0
    step_list = []
    for title, discription, pay in request.POST.get('procedure_steps'):
        step_list.append(ProcedureStep(procedure=procedure, title=title, discription=discription, pay=int(pay)))
        sum_pay += int(pay)

    # 检查支付金额比例是否合法
    if sum_pay != 100:
        return JsonResponse({'message': '所有步骤支付比例相加须为100%'})
    
    # 创建数据库条目
    procedure.save()
    for step in step_list:
        step.save()

    return JsonResponse({'success': True})
