from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import CooperationAppealing, CooperationPayment, Cooperation


@csrf_exempt
def backend(request):
    context = {}

    # 过滤出来所有还没有归还押金的项目
    on_deposit_client = Cooperation.objects.filter(client_deposit__gt=0)
    on_deposit_server = Cooperation.objects.filter(server_deposit__gt=0)
    on_deposit = on_deposit_client.union(on_deposit_server)
    context.update({'on_deposit': on_deposit})

    # 过滤出来所有处于未转移状态的付款
    transfering = CooperationPayment.objects.filter(transfer=False)
    context.update({'transfering': transfering})

    # 过滤出来所有申诉
    appealing = CooperationAppealing.objects.filter(is_finished=False)
    context.update({'appealing': appealing})

    return render(request, 'help/backend.html', context)
