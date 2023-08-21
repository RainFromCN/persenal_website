from alipay import AliPay
from alipay.exceptions import AliPayValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import User, Cooperation, CooperationPayment
from .mutex import _get_cooperation_lock

ALIPAY_NETWORK_GATE = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"

APPID = "9021000125639467"

APP_PUBLIC_KEY_STRING = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvv+olZHoxJw2hXMdqXt1g4pXiXaIJFcmdKLRFaD9yslXpV6CPVARkG0DITba/1v+/0mbSmrfy/OUpffzxyyk6sLcm/k1tmsyr/yvuh4y2PWeN2MYN8EhOjp7d20YPWv6wrC4wxKGj2Upu60iSpzv3nUE8sPS1MvR1qALhVUBx+cJIaxwLPVa2TYMhcfAagU7B/25y/+Li1g8vniAb+altBOgRLonuuuNCxD38rY8Yz0d/LUAXj4PviKVBSdWvmKfwKqV2i1yuH7G76tlwV8GlhpIKHQJLWySA1SY4pxuf/jEwt2CcYc0xKBrO1RdQ5S6Gjbl0vLtr/AF7tzkolbARwIDAQAB
-----END PUBLIC KEY-----"""

APP_PRIVATE_KEY_STRING = """-----BEGIN RSA PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC+/6iVkejEnDaFcx2pe3WDileJdogkVyZ0otEVoP3KyVelXoI9UBGQbQMhNtr/W/7/SZtKat/L85Sl9/PHLKTqwtyb+TW2azKv/K+6HjLY9Z43Yxg3wSE6Ont3bRg9a/rCsLjDEoaPZSm7rSJKnO/edQTyw9LUy9HWoAuFVQHH5wkhrHAs9VrZNgyFx8BqBTsH/bnL/4uLWDy+eIBv5qW0E6BEuie6640LEPfytjxjPR38tQBePg++IpUFJ1a+Yp/AqpXaLXK4fsbvq2XBXwaWGkgodAktbJIDVJjinG5/+MTC3YJxhzTEoGs7VF1DlLoaNuXS8u2v8AXu3OSiVsBHAgMBAAECggEAYe5uPzqQEfdS0TwEEnl1+Js/ZQE8rv1sf1NYR3HDj22LHgSGXO+oAdiTST16LoK6DaVtFUwVMdrT9gFbol1WtfRx7xtpmf3/AFNcut5vDeVqWVXa/gNtiRCha8upKR0rdxXrtkHScsXZDxynv4AWUYbIob0cZfWXwydOoO/EOP1t3A7bi1yI8qXuKkWzIwB0em7xIK3oAILFinzfCXU7P/JjxUKNrjkzX5bBqya7kTUxzx19se9taICrblI/3dThx1sqia4KGdBvbRQCxHOUG7wxIpuBxwWwK1twgGp0Q1opE/zEqsSyVZ5H2vUfqfibpM4CHT3e4ZuOtiTw+B0YqQKBgQD4W5GpeAQf8zJk5h+UZbiiOguCLK6mybzMotFR4xwFYDevuYoJPj+yfUWHLzf1Qpx8x2k4IcZIbDgkqqxMh/mqudc3HtRICbv1YvvRIr4TaglfJZm+aJPZMNfdjdYSEaO9UCJdQY0dbTHYhiqZffSjt6z2GsW9yG1P3IJ6bFN8UwKBgQDE4D7QaTMsHB7wBPtz69UF4KNwZ6frrZ5Ja4Nk9TTxXN/ZmY+1CvnHB5S3PerZblggJpM2o2n4s+kFuhIaYr5BXlaY5EEptWhi/tn0gDqR69k6gaAEKGpDBODK36xaudeY1gHUw4q7k23zzz+j09LrjSLA/IlG6nC4yT4LEJVNvQKBgDYERIQldFA2pulHG+s8zJGMKmCfs0TXb9baOsiiqr+Ik9QGeL1V6qi5klu6q2MOn9aL0JjCz8uErhlbfaoPkP/O974nWGhqpZTTeI2eDtVOJMeq9+tv92gvtWOcq8i2SXStbyv1S+nwi/zaAX3s5T6OfnHwlL2YUB4kicRytx29AoGBALsakxfmouds4kohsgf9PTqUvz94g7IMEr6cGwe7slEgfu2Cb30TrUZmAgQUKDn0EHSdtJLcwz3FXdQ/fiztYvsk+Q/c/cDx0v8iTWl85C0CBDUCNF0/O53t6OVlpZujuy5ZVOwr2pFiD8ECWe0Mxwtt2nWmi6CF9hLnzrsdS4fRAoGBAJy1teVIM1HNFYDm2tyAVXqIVFfWb0zemSSuMXnqbcL+6ssrvc//cPiiPJjbI8l4pgOgv+ReNS6qj0Brb+1IkcknDE3skTND+KA4Y0568dTsPT+qhdIohF2Q44jeQ3R13izyFTQmaIlNju6gEac2MU0D9bsqGm6JXRPXBz7CYWT6
-----END RSA PRIVATE KEY-----"""

ALIPAY_PUBLIC_KEY_STRING = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwH2JJWHf6JaclRSUP4Y25MSogyuK8vIm60pPo1SC/8VbF7TbQ9igTzp/BeRIs2xHKJCMFS+NfcBfn9YRTL+dkI1r4eWaUqcs6hml3SNAh/J8dK7YkpoT2nodjsQS/Qte2V6O/l9M2rgun6LIsK46opQ4zuPG3t7pyXcO3YKAGFCrdsVwRWJ2Z9cjMxf5wdU13KyQOJ56YUHPGgkRFDxfJjdzf7R+8Bri8h5gfkJT7CjgmXWq21fCI9EXRCbvzWp/K+KjGXJSJILKbeXAPO7etcD9ML/TsC/3kg9urfO+hDIheTQrxJd2oj3/RO+DBKiHkxuso5a+z6n2aEEFozvbZQIDAQAB
-----END PUBLIC KEY-----"""


ALIPAY = AliPay(
    appid=APPID, # 开发者的APPID
    app_notify_url=None,
    app_private_key_string=APP_PRIVATE_KEY_STRING,
    alipay_public_key_string=ALIPAY_PUBLIC_KEY_STRING,
    sign_type="RSA2",
    debug=True,
)


MESSAGE = None


@csrf_exempt
def check_payment(request):
    global MESSAGE

    t_id = request.POST.get('id')

    # 从数据库中获取数据
    transfer = CooperationPayment.objects.get(id=t_id)

    # 向远端进行请求
    payment_query_alipay(transfer.coop, transfer.step)
    
    # 返回查询结果
    return JsonResponse({'message': MESSAGE})


@csrf_exempt
def check_transfer(request):
    t_id = request.POST.get('id')

    # 从数据库中获取数据
    transfer = CooperationPayment.objects.get(id=t_id)

    out_biz_no = f"cooperation_{transfer.coop.id}_step_{transfer.step}_transfer"

    # 获取结果
    res = ALIPAY.api_alipay_fund_trans_order_query(out_biz_no=out_biz_no)

    # 排除异常
    if res is None:
        return JsonResponse({'message': '远端系统连接失败，请重试'})
    elif res['msg'] != 'Success':
        return JsonResponse({'message': f"错误原因：{res['sub_msg']}"})
    
    # 返回状态
    if res.get('status') == 'SUCCESS':
        return JsonResponse({'message': f"已转交成功，日期 {res['pay_date']}"})
    else:
        return JsonResponse({'message': f"未知状态：{res.get('status')}"})


@csrf_exempt
def transfer_payment(request):
    t_id = request.POST.get('id')

    # 从数据库中获取数据
    transfer = CooperationPayment.objects.get(id=t_id)

    # 排除异常
    if transfer.coop.server_alipay_id == '':
        return JsonResponse({'message': '数据库中没有竞方收款账号'})
    
    out_biz_no = f"cooperation_{transfer.coop.id}_step_{transfer.step}_transfer"

    # 付款
    res = ALIPAY.api_alipay_fund_trans_toaccount_transfer(
        out_biz_no=out_biz_no,
        payee_type="ALIPAY_USERID",
        payee_account=transfer.coop.server_alipay_id,
        amount=f"{transfer.amount:.2f}",
    )

    # 排除异常
    if res is None:
        return JsonResponse({'message': '远端系统连接失败，请重试'})
    elif res['msg'] != 'Success':
        return JsonResponse({'message': f"错误原因：{res['sub_msg']}"})
    
    # 返回成功
    transfer.transfer = True
    transfer.save()
    return JsonResponse({'success': True})


@csrf_exempt
def refund_deposit(request):
    coop_id = request.POST.get('coop_id')
    role = request.POST.get('role')
    try:
        _get_cooperation_lock(coop_id).acquire()
        # 从数据库中获取数据
        coop = Cooperation.objects.get(id=coop_id)
        user = coop.follow.user if role == 'server' else coop.follow.request.publisher

        # 系统退还押金
        out_trade_no = f"{user.name}.cooperation.{coop_id}.deposit"
        try:
            res = deposit_query_alipay(coop, user)
            if res is None:
                raise RuntimeError(MESSAGE)
            
            amount, _ = res # amount 本身就是字符串

            # 使用支付宝API退还押金
            ALIPAY.api_alipay_trade_refund(amount, out_trade_no)
            if role == 'client': 
                coop.client_deposit = '0'
            elif role == 'server':
                coop.server_deposit = '0'
            coop.save()
        except Exception as e:
            return JsonResponse({'message': f'{e}'})

        return JsonResponse({'success': True})
    finally:
        _get_cooperation_lock(coop_id).release()


def payment_query_alipay(coop, step):
    global ALIPAY, MESSAGE

    MESSAGE = ''

    # 获取订单编号
    out_trade_no = f"{coop.follow.request.publisher.name}.cooperation.{coop.id}.step.{step}.payment"

    # 获取响应
    try:
        if (res := ALIPAY.api_alipay_trade_query(out_trade_no=out_trade_no)) is None:
            MESSAGE = '与远端连接错误，请稍后重试'
            return None
    except AliPayValidationError:
        MESSAGE = '公钥验证错误'
        return None

    # 查看响应是否合法
    if res['msg'] != 'Success':
        MESSAGE = f"失败原因：{res.get('sub_msg')}"
        return None

    # 保存支付时间
    total_amount = res.get('total_amount')
    trade_status = res.get('trade_status')

    if trade_status == 'TRADE_SUCCESS':
        # 如果支付成功则返回支付金额
        datetime = res.get('send_pay_date').split(' ')
        date_part = [int(part) for part in datetime[0].split('-')]
        time_part = [int(part) for part in datetime[1].split(':')]
        datetime = timezone.datetime(*date_part, *time_part)
        MESSAGE = f"已付款 {total_amount} 元，付款日期 {datetime}"
        return total_amount, datetime
    else:
        # 其他的状态
        MESSAGE = f"未知状态：{trade_status}"

    # 支付不成功返回null
    return None


@csrf_exempt
def check_deposit(request):
    coop_id = request.POST.get('coop_id')
    coop = Cooperation.objects.get(id=coop_id)

    # 检查client的押金
    client = coop.follow.request.publisher
    deposit_query_alipay(coop, client)
    client_message = MESSAGE

    # 检查server的押金
    server = coop.follow.user
    deposit_query_alipay(coop, server)
    server_message = MESSAGE

    return JsonResponse({'message': f'竞方:{server_message}\n 需方:{client_message}'})


def deposit_query_alipay(coop, user):
    global ALIPAY, MESSAGE

    MESSAGE = ''
    out_trade_no = f"{user.name}.cooperation.{coop.id}.deposit"

    # 获取响应
    try:
        if (res := ALIPAY.api_alipay_trade_query(out_trade_no=out_trade_no)) is None:
            MESSAGE = '与远端连接错误，请稍后重试'
            return None
    except AliPayValidationError:
        MESSAGE = '公钥验证错误'
        return None
    
    # 查看响应是否合法
    if res['msg'] != 'Success':
        MESSAGE = f"远端查找失败，原因：{res['sub_msg']}"
        return None

    total_amount = res.get('total_amount')
    trade_status = res.get('trade_status')
    buyer_user_id = res.get('buyer_user_id')

    # 如果支付成功则返回支付金额
    if trade_status == 'TRADE_SUCCESS':
        MESSAGE = f"已支付押金 {total_amount} 元，仍未退还"
        return total_amount, buyer_user_id
    elif trade_status == 'TRADE_CLOSED':
        MESSAGE = f"押金已全部退还"
    else:
        MESSAGE = f"未知押金状态：{trade_status}"

    # 支付不成功返回null
    return None


@csrf_exempt
def get_deposit_pay_link(request):
    pay_method = request.POST.get('pay_method')

    c_id = int(request.POST.get('cooperation_id'))
    username = request.POST.get('username')

    user = User.objects.get(name=username)
    coop = Cooperation.objects.get(id=c_id)

    # 检查是否已经支付
    cond1 = user == coop.follow.user and float(coop.server_deposit) > 0
    cond2 = user == coop.follow.request.publisher and float(coop.client_deposit) > 0
    if cond1 or cond2:
        return JsonResponse({'message': '佣金已经支付'})

    # 计算需要支付多少押金
    bid_price = coop.follow.bid_price
    deposit = 0.1 * bid_price

    if pay_method == 'alipay':
        try:
            global ALIPAY

            # 发起支付，网页支付
            order_string = ALIPAY.api_alipay_trade_page_pay(
                out_trade_no=f"{username}.cooperation.{c_id}.deposit", 
                product_code="FAST_INSTANT_TRADE_PAY",
                total_amount=f"{deposit:.2f}",
                subject="押金")

            return JsonResponse({'url': f"{ALIPAY_NETWORK_GATE}?{order_string}",
                                 'success': True})
        except Exception as e:
            return JsonResponse({'message': e})
    else:
        return JsonResponse({'message': f'尚不支持{pay_method}'})


@csrf_exempt
def get_pay_link(request):
    coop_id = request.POST.get('cooperation_id')
    username = request.POST.get('username')
    
    # 从数据库中获取
    coop = Cooperation.objects.get(id=coop_id)
    user = User.objects.get(name=username)

    # 确认该用户是否是合作的需求方
    if coop.follow.request.publisher != user:
        return JsonResponse({'message': '系统出错，请重新登陆'})

    # 计算需要付款的价格
    price = float(coop.follow.procedure.procedurestep_set.all()[coop.active].pay) / 100 * float(coop.follow.bid_price)

    # 设置填写参数
    out_trade_no = f"{username}.cooperation.{coop_id}.step.{coop.active}.payment"
    amount = f"{price:.2f}"

    try:
        # 向支付宝申请二维码
        res = ALIPAY.api_alipay_trade_page_pay(
            subject="需方付款",
            out_trade_no=out_trade_no, 
            total_amount=amount,
            product_code="FAST_INSTANT_TRADE_PAY",
        )
    except Exception:
        return JsonResponse({'message': '系统出错，请稍后重试'})

    return JsonResponse({'success': True, 'url': f"{ALIPAY_NETWORK_GATE}?{res}"})
