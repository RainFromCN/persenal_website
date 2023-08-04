from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from project.models import User, ALL_FIELDS
from .models import Request, REQUEST_TYPE, RequestFollows


current_field = 0  # 用来记录当前的field


# Create your views here.
@csrf_exempt
def index(request):
    global current_field

    if request.method == 'POST':
        current_field = int(request.POST.get('field')) - 1
        return JsonResponse({})
    
    context = {
        'request': Request.objects.filter(field=ALL_FIELDS[current_field][1], state=0).order_by('datetime').reverse()
    }
    
    # 计算时间
    now = timezone.now()
    for rqst in context['request']:
        delta = now - rqst.datetime.astimezone(timezone.utc)
        delta_days = delta.days
        delta_seconds = delta.seconds
        if delta_days > 365:
            rqst.timedelta = f"{delta_days // 365} 年前发布"
        elif delta_days > 30:
            rqst.timedelta = f"{delta_days // 30} 月前发布"
        elif delta_days > 0:
            rqst.timedelta = f"{delta_days} 天前发布"
        elif delta_seconds > 3600:
            rqst.timedelta = f"{delta_seconds // 3600} 小时前发布"
        else:
            rqst.timedelta = "刚刚发布"
    
    # 查看用户登录状态
    if 'username' in request.session:
        context['username'] = request.session['username']
        context['usr'] = User.objects.filter(name=context['username']).first()

        # 加入我发布的需求和竞标
        my_requests = Request.objects.filter(publisher=context['usr']).reverse()
        my_follows = RequestFollows.objects.filter(user=context['usr']).reverse()
        context.update({
            'my_requests': my_requests,
            'my_follows': my_follows,
        })

    context['all_fields'] = ALL_FIELDS
    context['all_request_type'] = REQUEST_TYPE
    context['current_field'] = current_field + 1
    return render(request, "help/index.html", context)


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
    if 'username' in request.session:
        del request.session['username']
    return JsonResponse({})


@csrf_exempt
def request_publish(request):
    if 'username' not in request.session:
        return JsonResponse({'message': '请先登录'})
    user = User.objects.filter(name=request.session['username']).first()

    if request.POST.get('title') == '' or request.POST.get('detail') == '' or request.POST.get('field') == '' or request.POST.get('type') == '':
        return JsonResponse({'message', '请按照要求的格式填写'})

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
def detail(request, request_id):
    rqst = Request.objects.filter(id=request_id).first()
    follows = RequestFollows.objects.filter(request=rqst).order_by('state').reverse()
    context = {
        'follows': follows,
        'rqst': rqst,
        'all_fields': ALL_FIELDS,
        'all_request_type': REQUEST_TYPE,
    }
    delta = timezone.now() - rqst.datetime.astimezone(timezone.utc)
    delta_days = delta.days
    delta_seconds = delta.seconds
    if delta_days > 365:
        rqst.timedelta = f"{delta_days // 365} 年前发布"
    elif delta_days > 30:
        rqst.timedelta = f"{delta_days // 30} 月前发布"
    elif delta_days > 0:
        rqst.timedelta = f"{delta_days} 天前发布"
    elif delta_seconds > 3600:
        rqst.timedelta = f"{delta_seconds // 3600} 小时前发布"
    else:
        rqst.timedelta = "刚刚发布"

    if 'username' in request.session:
        context['username'] = request.session['username']
        context['usr'] = User.objects.filter(name=context['username']).first()
        # 加入我发布的需求和竞标
        my_requests = Request.objects.filter(publisher=context['usr']).reverse()
        my_follows = RequestFollows.objects.filter(user=context['usr']).reverse()
        context.update({
            'my_requests': my_requests,
            'my_follows': my_follows,
        })
    return render(request, "help/detail.html", context)


@csrf_exempt
def bidding(request, request_id):
    if 'username' not in request.session:
        return JsonResponse({'message': '请先登录'})
    user = User.objects.filter(name=request.session['username']).first()
    rqst = Request.objects.filter(id=request_id).first()

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
    if 'username' not in request.session:
        return JsonResponse({'message': '请先登录'})
    user = User.objects.filter(name=request.session['username']).first()
    
    tel = request.POST.get('tel')
    intro = request.POST.get('introduction')

    user.tel = tel
    user.introduction = intro

    user.save()

    return JsonResponse({'success': True})


@csrf_exempt
def cooperation(request):
    print(request.POST.get('id'))
    # 获取follow
    follow_id = request.POST.get('id')
    follow = RequestFollows.objects.filter(id=follow_id).first()
    follow.state = 1
    follow.save()

    # 更改状态
    follow.request.state = 1
    follow.user.win_times += 1
    follow.request.save()
    follow.user.save()

    return JsonResponse({"success": True})
