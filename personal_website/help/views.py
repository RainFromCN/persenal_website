from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import pytz

from markdown import markdown

from project.models import User, ALL_FIELDS
from .models import (
    Request, 
    REQUEST_TYPE,
    RequestFollows,
    Procedure,
    ProcedureStep,
    Cooperation,
)


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

            # 为用户创建默认流程
            procedure = Procedure(name='工程外包流程（平台提供）', owner=user)
            procedure.save()
            steps = [
                ProcedureStep(procedure=procedure, title='确认需求', discription='双方确认详细需求清单，并提交给平台', pay=0),
                ProcedureStep(procedure=procedure, title='服务商完成初稿', discription='快速实现核心功能', pay=0),
                ProcedureStep(procedure=procedure, title='初稿验收合格', discription='若验收满意需支付30%费用，不满意则无需支付并终止服务', pay=30),
                ProcedureStep(procedure=procedure, title='服务商完成终稿', discription='实现全部功能', pay=0),
                ProcedureStep(procedure=procedure, title='终稿验收合格', discription='验收满意需再支付40%的费用', pay=70),
            ]
            for step in steps:
                step.save()
            
            procedure = Procedure(name='作业指导流程（平台提供）', owner=user)
            procedure.save()
            steps = [
                ProcedureStep(procedure=procedure, title='确认需求', discription='双方确认详细需求清单，并提交给平台', pay=0),
                ProcedureStep(procedure=procedure, title='服务商完成作业', discription='实现作业要求的各项功能', pay=0),
                ProcedureStep(procedure=procedure, title='作业验收合格', discription='查看完成的作业是否符合要求，不满意则无需支付并终止服务', pay=30),
                ProcedureStep(procedure=procedure, title='服务商讲解', discription='针对作业实现细节进行辅导讲解', pay=0),
                ProcedureStep(procedure=procedure, title='讲解完毕', discription='讲解满意再支付剩余70%的费用', pay=70),
            ]
            for step in steps:
                step.save()

            procedure = Procedure(name='科研指导流程（平台提供）', owner=user)
            procedure.save()
            steps = [
                ProcedureStep(procedure=procedure, title='确认需求', discription='双方确认详细需求清单，并提交给平台', pay=0),
                ProcedureStep(procedure=procedure, title='服务商发掘创新点并进行实验', discription='阅读大量文献，寻找论文创新点，并在平台实时更新研究进度', pay=0),
                ProcedureStep(procedure=procedure, title='实验结果验收', discription='若验收满意需要支付30%费用，不满意则无需支付并终止服务', pay=30),
                ProcedureStep(procedure=procedure, title='服务商讲解实验细节', discription='针对实验细节进行辅导讲解', pay=0),
                ProcedureStep(procedure=procedure, title='讲解完毕', discription='讲解满意再支付剩余70%的费用', pay=70),
            ]
            for step in steps:
                step.save()

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
        # 加入这个用户的所有流程
        context['procedures'] = Procedure.objects.filter(owner=context['usr'])
        print('ok')
        # 加入合作选项
        if context['follows'].count() > 0 and context['follows'].first().state == 1:
            context['cooperation'] = Cooperation.objects.get(follow=context['follows'].first())

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
    procedure_id = int(request.POST.get('procedure_id'))

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
def make_cooperation(request):
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

    # 创建Cooperation
    cooperation = Cooperation(follow=follow)
    cooperation.save()

    return JsonResponse({"success": True})


@csrf_exempt
def create_procedures(request):
    if 'username' not in request.session:
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


@csrf_exempt
def cooperation(request, cooperation_id):
    context = {
        'cooperation': Cooperation.objects.get(id=cooperation_id)
    }
    if 'username' in request.session:
        context['usr'] = User.objects.get(name=request.session['username'])
    print(context['cooperation'].request_document)
    return render(request, 'help/cooperation.html', context)


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

    # 修改合作的表项
    cooperation = Cooperation.objects.get(id=int(cooperation_id))
    cooperation.request_document = document
    cooperation.request_document_update = True
    cooperation.request_document_update_datetime = timezone.now()
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
def submit_finish_date(request):

    # 从前端获取数据
    finish_date = request.POST.get('finish_date')
    cooperation_id = request.POST.get('cooperation_id')
    date_parts = [int(x) for x in finish_date.split('T')[0].split('-')]
    date = timezone.datetime(*date_parts) + timezone.timedelta(days=1)
    if timezone.datetime.today() > date:
        return JsonResponse({'message': '预计完成日期应该在今天之后'})

    # 保存完成日期
    cooperation = Cooperation.objects.get(id=int(cooperation_id))
    cooperation.predict_finish_date = f"{date}"
    cooperation.save()

    return JsonResponse({'success': True})
    