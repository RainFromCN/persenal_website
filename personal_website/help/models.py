from django.db import models

from project.models import User, ALL_FIELDS
from django.utils import timezone


REQUEST_TYPE = (
    (1, '作业指导'),
    (2, '工程外包'),
    (3, '科研指导'),
)


# Create your models here.
class Request(models.Model):
    id = models.AutoField(primary_key=True) # 需求的id
    publisher = models.ForeignKey(to=User, on_delete=models.CASCADE)  # 发布者
    datetime = models.DateTimeField(auto_now_add=True) # 发布时间
    title = models.CharField(max_length=20)  # 需求的标题
    content = models.CharField(max_length=200)  # 需求内容
    field = models.CharField(max_length=20)  # 需求所在领域
    type = models.CharField(max_length=20) # 需求的类型

    # 状态
    state = models.IntegerField(default=0)  # 该需求的状态，0代表尚未解决，1代表已经解决
    num_bid = models.IntegerField(default=0)  # 有多少人竞标
    num_comment = models.IntegerField(default=0)  # 有多少人评论
    lowest_bid = models.CharField(default='-', max_length=10)  # 当前最低价


class Procedure(models.Model):
    id = models.AutoField(primary_key=True) # 流程的ID
    name = models.CharField(max_length=50) # 流程的名字
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)  # 流程所有者


class ProcedureStep(models.Model):
    procedure = models.ForeignKey(to=Procedure, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)  # 步骤的标题
    discription = models.CharField(max_length=100)  # 步骤的详细解读
    pay = models.IntegerField()  # 需要支付的百分比


class ProcedureSubstep(models.Model):
    step = models.ForeignKey(to=ProcedureStep, on_delete=models.CASCADE)
    type = models.BooleanField()
    content = models.CharField(max_length=100) # 本步骤的内容


class RequestFollows(models.Model):
    id = models.AutoField(primary_key=True) # 跟随的ID
    request = models.ForeignKey(to=Request, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    bid_price = models.IntegerField()  # 竞标价格
    procedure = models.ForeignKey(to=Procedure, on_delete=models.CASCADE)

    # 状态
    state = models.IntegerField(default=0)  # 竞标状态，0表示未中标，1表示中标


class Cooperation(models.Model):
    id = models.AutoField(primary_key=True)
    follow = models.ForeignKey(to=RequestFollows, on_delete=models.CASCADE)
    active = models.IntegerField(default=0)  # 当前激活的步骤
    is_appeal = models.BooleanField(default=False) # 是否处于申诉状态

    # 有关需求文档
    request_document = models.CharField(max_length=2000, default='# 这是一级标题\n## 这是二级标题\n### 这是三级标题\n这是正文')  # 需求文档
    request_document_update_datetime = models.DateTimeField(null=True)
    request_document_update = models.BooleanField(default=False)  # 需求文档是否曾被更新过

    # 押金相关
    client_deposit = models.DecimalField(default=0.0, max_digits=8, decimal_places=2)
    server_deposit = models.DecimalField(default=0.0, max_digits=8, decimal_places=2)
    client_alipay_id = models.CharField(max_length=30, default='', blank=True)
    server_alipay_id = models.CharField(max_length=30, default='', blank=True)
    client_wechat_id = models.CharField(max_length=30, default='', blank=True)
    server_wechat_id = models.CharField(max_length=30, default='', blank=True)

    # 退还押金相关
    client_cancel = models.BooleanField(default=False) # 需求方主动终止
    server_cancel = models.BooleanField(default=False) # 服务方主动终止


# 需求方给服务商的评价
class ClientFeedback(models.Model):
    target = models.ForeignKey(to=User, on_delete=models.CASCADE) # 服务商，方便查表
    coop = models.ForeignKey(to=Cooperation, on_delete=models.CASCADE)
    rate = models.FloatField()
    review = models.CharField(max_length=100)
    date = models.DateField()


# 服务商给需求方的评价
class ServerFeedback(models.Model):
    target = models.ForeignKey(to=User, on_delete=models.CASCADE) # 需求方
    coop = models.ForeignKey(to=Cooperation, on_delete=models.CASCADE)
    rate = models.FloatField()
    review = models.CharField(max_length=100)
    date = models.DateField()


# 申诉
class CooperationAppealing(models.Model):
    coop = models.ForeignKey(to=Cooperation, on_delete=models.CASCADE)
    initiator = models.ForeignKey(to=User, on_delete=models.CASCADE)

    mobile = models.CharField(max_length=11)
    reason = models.CharField(max_length=200)
    expect_result = models.CharField(max_length=200)

    result = models.CharField(max_length=200, default='', blank=True)
    is_finished = models.BooleanField(default=False)


class CooperationPayment(models.Model):
    id = models.AutoField(primary_key=True) # 付款ID
    coop = models.ForeignKey(to=Cooperation, on_delete=models.CASCADE)

    step = models.IntegerField() # 第几步支付的
    amount = models.DecimalField(max_digits=8, decimal_places=2)  # 支付金额
    datetime = models.DateTimeField()  # 支付时间

    transfer = models.BooleanField(default=False) # 是否已经移交给对方
