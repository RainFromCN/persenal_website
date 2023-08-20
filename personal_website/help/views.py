from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from markdown import markdown

from project.models import User, ALL_FIELDS
from .models import (
    Request, 
    REQUEST_TYPE,
    RequestFollows,
    Procedure,
    ProcedureStep,
    Cooperation,
    ServerFeedback,
    ClientFeedback,
    CooperationAppealing,
    CooperationPayment,
)

from . import steps, buy
from .mutex import _get_cooperation_lock


current_field = 0  # 用来记录当前的field


def _check_login(request):
    if 'username' in request.session:
        return True
    return False


def _get_login(request):
    user = User.objects.get(name=request.session['username'])
    user.save()
    return user


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
    if _check_login(request):
        context['username'] = request.session['username']
        context['usr'] = _get_login(request)

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

            # 为用户创建默认流程
            steps.generate_default_procedure(user)

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
            user.save() # 触发auto_now字段，更新用户登录时间
            return JsonResponse({'success': True})


@csrf_exempt
def exit(request):
    if 'username' in request.session:
        del request.session['username']
    return JsonResponse({})


@csrf_exempt
def request_publish(request):
    if not _check_login(request):
        return JsonResponse({'message': '请先登录'})
    user = _get_login(request)

    # 需求发布格式检查
    if request.POST.get('title') == '' or request.POST.get('detail') == '' or request.POST.get('field') == '' or request.POST.get('type') == '':
        return JsonResponse({'message', '请按照要求的格式填写'})

    # 查看该用户是否发布标题相同的需求
    if Request.objects.filter(publisher=user, title=request.POST.get('title')).count() > 0:
        return JsonResponse({'message': '请勿重复发布需求'})

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


def append_rate_and_review(follow: RequestFollows):
    if (query_set := follow.user.clientfeedback_set.all()).count() > 0:
        score = 0
        for feedback in query_set:
            score += feedback.rate * 20
        follow.rate = f"{score / query_set.count():.2f}"
        follow.feedbacks = query_set
    else:
        follow.rate = "-"
        follow.reviews = []


@csrf_exempt
def detail(request, request_id):
    rqst = Request.objects.filter(id=request_id).first()
    follows = RequestFollows.objects.filter(request=rqst).order_by('state').reverse()
    
    # 给所有的竞标者计算竞方好评率
    for follow in follows:
        append_rate_and_review(follow)

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

    if _check_login(request):
        context['username'] = request.session['username']
        context['usr'] = _get_login(request)

        # 加入我发布的需求和竞标
        my_requests = Request.objects.filter(publisher=context['usr']).reverse()
        my_follows = RequestFollows.objects.filter(user=context['usr']).reverse()

        # 将竞标者和需求加入上下文
        context.update({
            'my_requests': my_requests,
            'my_follows': my_follows,
        })

        # 加入这个用户的所有流程
        context['procedures'] = Procedure.objects.filter(owner=context['usr'])

        # 加入合作选项
        if context['follows'].count() > 0 and context['follows'].first().state == 1:
            context['cooperation'] = Cooperation.objects.get(follow=context['follows'].first())

    return render(request, "help/detail.html", context)


@csrf_exempt
def bidding(request, request_id):
    if not _check_login(request):
        return JsonResponse({'message': '请先登录'})
    user = _get_login(request)
    rqst = Request.objects.filter(id=request_id).first()

    # 格式检查
    if user.tel == '' or user.introduction == '':
        return JsonResponse({'message': '请先完善个人资料'})
    
    # 从前端获取数据
    bid_price = int(request.POST.get('bid'))
    procedure_id = int(request.POST.get('procedure_id'))

    # 检查该用户是否已经竞标
    if RequestFollows.objects.filter(request=rqst, user=user).count() > 0:
        return JsonResponse({'message': '请勿重复竞标'})

    # 创建投标信息
    follow = RequestFollows(request=rqst, user=user, bid_price=bid_price, procedure_id=procedure_id)
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
    if not _check_login(request):
        return JsonResponse({'message': '请先登录'})
    user = _get_login(request)
    
    tel = request.POST.get('tel')
    intro = request.POST.get('introduction')

    user.tel = tel
    user.introduction = intro

    user.save()

    return JsonResponse({'success': True})


@csrf_exempt
def make_cooperation(request):
    # 获取follow
    follow_id = request.POST.get('id')
    follow = RequestFollows.objects.filter(id=follow_id).first()

    # 检查follow是否已经中标
    if follow.state == 1:
        return JsonResponse({'message': '您已中标，请勿重复操作'})

    # 更改状态
    follow.state = 1
    follow.request.state = 1
    follow.user.win_times += 1
    cooperation = Cooperation(follow=follow)

    # xie 写数据库
    follow.request.save()
    follow.user.save()
    follow.save()
    cooperation.save()

    return JsonResponse({"success": True})

@csrf_exempt
def cooperation(request, cooperation_id):
    # 获取锁
    try:
        _get_cooperation_lock(cooperation_id).acquire()
        # 将合作加入上下文
        coop = Cooperation.objects.get(id=cooperation_id)
        context = {'cooperation': coop}

            # 将用户加入上下文
        if _check_login(request):
            context['usr'] = _get_login(request)

        # 将子步骤加入上下文
        active_step = coop.active
        substeps = coop.follow.procedure.procedurestep_set.all()[active_step].proceduresubstep_set.all()
        context['substeps'] = substeps

        # 查看是否已经支付押金
        if coop.active == 1:
            client = coop.follow.request.publisher
            server = coop.follow.user
            if float(coop.client_deposit) == 0:
                if res := buy.deposit_query_alipay(coop, client):
                    total_amount, buyer_user_id = res
                    coop.client_deposit = f"{total_amount}"
                    coop.client_alipay_id = buyer_user_id
                    coop.save()
            if float(coop.server_deposit) == 0:
                if res := buy.deposit_query_alipay(coop, server):
                    total_amount, buyer_user_id = res
                    coop.server_deposit = f"{total_amount}"
                    coop.server_alipay_id = buyer_user_id
                    coop.save()
            if float(coop.client_deposit) > 0 and float(coop.server_deposit) > 0:
                coop.active += 1
                coop.save()

        # 查看是否已经支付步骤2的金钱
        if coop.active == 2:
            if res := buy.payment_query_alipay(coop, coop.active):
                amount, datetime = res
                CooperationPayment(coop=coop, step=coop.active, amount=amount, datetime=datetime).save()
                coop.active += 1
                coop.save()
    finally:
        _get_cooperation_lock(cooperation_id).release()


    return render(request, 'help/cooperation.html', context)   


@csrf_exempt
def submit_cancel_cooperation(request):
    cid = int(request.POST.get('cooperation_id'))
    username = request.POST.get('username')

    try:
        _get_cooperation_lock(cid).acquire()
        # 从数据库中获取记录
        coop = Cooperation.objects.get(id=cid)
        user = User.objects.get(name=username)

        # 取消合作
        if coop.follow.user == user:
            if coop.server_cancel == False:
                coop.server_cancel = True
                coop.active = 4
                coop.save()
            else:
                return JsonResponse({'message': '请勿重复取消合作'})
        elif coop.follow.request.publisher == user:
            if coop.client_cancel == False:
                coop.client_cancel = True
                coop.active = 4
                coop.save()
            else:
                return JsonResponse({'message': '请勿重复取消合作'})
        
        # 返回成功信息
        return JsonResponse({'success': True})
    finally:
        _get_cooperation_lock(cid).release()


def _convert_document(document: str):
    html = markdown(document)
    return html


@csrf_exempt
def convert_md_to_html(request):
    document = request.POST.get('document')
    document = _convert_document(document)
    return JsonResponse({'html_document': document,
                         'success': True})


@csrf_exempt
def submit_request_document(request):

    # 从前端获取数据
    document = request.POST.get('request_document')
    cooperation_id = request.POST.get('cooperation_id')

    if '`' in document:
        return JsonResponse({'message': '文档中不能含有符号“`”'})

    # 修改合作的表项
    cooperation = Cooperation.objects.get(id=int(cooperation_id))
    cooperation.request_document = document
    cooperation.request_document_update = True
    cooperation.request_document_update_datetime = timezone.now() + timezone.timedelta(hours=8)
    cooperation.save()

    return JsonResponse({'success': True})


@csrf_exempt
def entry_next_step(request):
    
    # 从前端获取数据
    active_step = request.POST.get('active_step')
    cooperation_id = request.POST.get('cooperation_id')

    # 进入下一环节
    cooperation = Cooperation.objects.get(id=int(cooperation_id))        
    cooperation.active = int(active_step) + 1
    cooperation.save()

    return JsonResponse({'success': True})


@csrf_exempt
def submit_rate_and_review(request):
    username = request.POST.get('username')
    coop_id = int(request.POST.get('cooperation_id'))
    rate = float(request.POST.get('rate'))
    review = request.POST.get('review')

    try:
        _get_cooperation_lock(coop_id).acquire()
        user = User.objects.get(name=username)
        coop = Cooperation.objects.get(id=coop_id)

        # 检查评分和评价是否合法
        if rate == 0:
            return JsonResponse({'message': '请给对方打分'})
        elif rate < 0 or rate > 5:
            return JsonResponse({'message': '分数应该在1颗星到5颗星之间'})
        elif len(review) < 20:
            return JsonResponse({'message': '评论应不少于20个字'})
        
        # 查看角色
        if user == coop.follow.user:
            # 竞争者
            total_amount = f"{coop.server_deposit}"
            cancel = coop.server_cancel
            role = 'server'
        elif user == coop.follow.request.publisher:
            # 需求方
            total_amount = f"{coop.client_deposit}"
            cancel = coop.client_cancel
            role = 'client'
        else:
            return JsonResponse({"message": "系统出错，请关闭所有网站并重新登陆后再试"})

        # 系统退还押金
        out_trade_no = f"{username}.cooperation.{coop_id}.deposit"
        if cancel == False and float(total_amount) > 0:
            try:
                # 使用支付宝API退还押金
                buy.ALIPAY.api_alipay_trade_refund(total_amount, out_trade_no)
                if role == 'client': 
                    coop.client_deposit = '0'
                elif role == 'server':
                    coop.server_deposit = '0'            
            except Exception:
                return JsonResponse({'message': '系统繁忙，请稍后再试'})
        
        # 转换为上海时区之后，取日期
        date = (timezone.now() + timezone.timedelta(hours=8)).date()

        # 将评论加入数据库
        if role == 'client':
            ClientFeedback(target=coop.follow.user, coop=coop, rate=rate, review=review, date=date).save()
        elif role == 'server':
            ServerFeedback(target=coop.follow.request.publisher, coop=coop, rate=rate, review=review, date=date).save()
        coop.save()

        # 返回成功
        return JsonResponse({'success': True})
    finally:
        _get_cooperation_lock(coop_id).release()


@csrf_exempt
def submit_appeal(request):
    coop_id = request.POST.get('cooperation_id')
    username = request.POST.get('username')
    mobile = request.POST.get('mobile')
    reason = request.POST.get('reason')
    result = request.POST.get('result')

    try:
        _get_cooperation_lock(coop_id).acquire()

        # 从数据库中获取数据
        user = User.objects.get(name=username)
        coop = Cooperation.objects.get(id=coop_id)

        # 检查是否已经申诉
        if CooperationAppealing.objects.filter(coop=coop).count() > 0:
            return JsonResponse({'message': '请勿重复申诉'})

        # 创建合作申诉对象并保存
        coop.is_appeal = True
        appeal = CooperationAppealing(coop=coop, initiator=user, mobile=mobile,
                                    expect_result=result, reason=reason)
        coop.save()
        appeal.save()

        # 申诉成功，返回
        return JsonResponse({'success': True})
    finally:
        _get_cooperation_lock(coop_id).release()


@csrf_exempt
def remove_appeal(request):
    coop_id = request.POST.get('cooperation_id')
    username = request.POST.get('username')

    # 从数据库中获取数据
    user = User.objects.get(name=username)
    coop = Cooperation.objects.get(id=coop_id)

    # 检查是否已经申诉
    if CooperationAppealing.objects.filter(coop=coop, initiator=user).count() == 0:
        return JsonResponse({'message': '申诉不存在'})
    
    # 检查合作的is_appeal字段
    if coop.is_appeal == False:
        return JsonResponse({'message': "申诉不存在"})
    
    # 删除
    appeal = CooperationAppealing.objects.filter(coop=coop, initiator=user).first()
    appeal.delete()
    coop.is_appeal = False
    coop.save()

    return JsonResponse({"success": True})


@csrf_exempt
def submit_appeal_result(request):
    coop_id = int(request.POST.get('coop_id'))
    result = request.POST.get('result')
    coop = Cooperation.objects.get(id=coop_id)

    # 检查数据
    if (not isinstance(result, str)) or len(result) < 20:
        return JsonResponse({'message': '申诉结果应大于20字'})

    # 从数据库找到申诉对象
    appeal = coop.cooperationappealing_set.all().first()
    appeal.result = result
    appeal.is_finished = True
    appeal.save()

    return JsonResponse({'success': True})


# @csrf_exempt
# def submit_finish_date(request):

#     # 从前端获取数据
#     finish_date = request.POST.get('finish_date')[:10]
#     cooperation_id = request.POST.get('cooperation_id')
#     date_parts = [int(x) for x in finish_date.split('-')]
#     date = timezone.datetime(*date_parts) + timezone.timedelta(days=1)
#     if timezone.datetime.today() > date:
#         return JsonResponse({'message': '预计完成日期应该在今天之后'})
    
#     # 响应字典
#     response = {'success': True}

#     # 设置相应字段
#     cooperation = Cooperation.objects.get(id=int(cooperation_id))
#     response['fix'] = True
#     cooperation.predict_finish_date_fix = (f"{date}")[:10]
#     cooperation.predict_finish_date_fix_state = 0

#     # 保存日期
#     cooperation.save()

#     return JsonResponse(response)
    

# @csrf_exempt
# def submit_fix_finish_date(request):
#     # 从前端获取数据
#     agree = int(request.POST.get('agree'))
#     cooperation_id = request.POST.get('cooperation_id')

#     # 设置相应字段
#     cooperation = Cooperation.objects.get(id=int(cooperation_id))
#     if agree == 1:
#         cooperation.predict_finish_date = cooperation.predict_finish_date_fix
#         cooperation.predict_finish_date_fix_state = 1
#     elif agree == 0:
#         cooperation.predict_finish_date_fix_state = 2
#     cooperation.predict_finish_date_fix = ''
#     cooperation.save()

#     return JsonResponse({'success': True})


# @csrf_exempt
# def submit_acceptance_date(request):

#     # 从前端获取数据
#     acceptance_date = request.POST.get('acceptance_date')
#     cooperation_id = request.POST.get('cooperation_id')
#     date_parts = [int(x) for x in acceptance_date[:10].split('-')]
#     time_parts = [int(x) for x in acceptance_date[11:19].split(':')]

#     # 转换为上海时区
#     date = timezone.datetime(*date_parts, *time_parts) + timezone.timedelta(hours=8)

#     if timezone.datetime.today() > date:
#         return JsonResponse({'message': '验收日期应该在今天之后'})
#     elif date > timezone.datetime.today() + timezone.timedelta(days=7):
#         return JsonResponse({'message': '验收日期必须在未来七天之内'})
        
#     # 响应字典
#     response = {'success': True}

#     # 设置相应字段
#     cooperation = Cooperation.objects.get(id=int(cooperation_id))
#     response['fix'] = True
#     cooperation.acceptance_date_fix = (f"{date}")
#     cooperation.acceptance_date_fix_state = 0

#     # 保存日期
#     cooperation.save()

#     return JsonResponse(response)
    

# @csrf_exempt
# def submit_fix_acceptance_date(request):
#     # 从前端获取数据
#     agree = int(request.POST.get('agree'))
#     cooperation_id = request.POST.get('cooperation_id')

#     # 设置相应字段
#     cooperation = Cooperation.objects.get(id=int(cooperation_id))
#     if agree == 1:
#         cooperation.acceptance_date = cooperation.acceptance_date_fix
#         cooperation.acceptance_date_fix_state = 1
#     elif agree == 0:
#         cooperation.acceptance_date_fix_state = 2
#     cooperation.acceptance_date_fix = ''
#     cooperation.save()

#     return JsonResponse({'success': True})
