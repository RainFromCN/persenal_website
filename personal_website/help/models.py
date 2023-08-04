from django.db import models

from project.models import User
from .utils import REQUEST_TYPE, ALL_FIELDS


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
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)  # 流程所有者
    

class ProcedureStep(models.Model):
    procedure = models.ForeignKey(to=Procedure)
    title = models.CharField(max_length=20)  # 步骤的标题
    discription = models.CharField(max_length=100)  # 步骤的详细解读
    pay = models.IntegerField()  # 需要支付的百分比


class RequestFollows(models.Model):
    id = models.AutoField(primary_key=True) # 跟随的ID
    request = models.ForeignKey(to=Request, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    bid_price = models.IntegerField()  # 竞标价格
    notify_new_bids = models.BooleanField()  # 当有新的竞标时是否通知

    # 状态
    state = models.IntegerField(default=0)  # 竞标状态，0表示未中标，1表示中标
    

class RequestFollowsChatMessage(models.Model):
    publisher = models.ForeignKey(to=User, on_delete=models.CASCADE)
    follow = models.ForeignKey(to=RequestFollows, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)  # 发表的文字

