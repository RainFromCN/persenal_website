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

    # 有关需求文档
    request_document = models.CharField(max_length=2000, default='# 这是一级标题\n## 这是二级标题\n### 这是三级标题\n这是正文')  # 需求文档
    request_document_update_datetime = models.DateTimeField(default=timezone.now())
    request_document_update = models.BooleanField(default=False)  # 需求文档是否曾被更新过

    # 有关项目验收
    predict_finish_date = models.CharField(default='', max_length=20, blank=True) # 项目预计完成日期
    predict_finish_date_fix = models.CharField(default='', max_length=20, blank=True)  # 提交的修改
    predict_finish_date_fix_state = models.IntegerField(default=0)  # 0表示未做出响应，1表示同意，2表示拒绝

class CooperationMessage(models.Model):
    cooperation = models.ForeignKey(to=Cooperation, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    img_id = models.CharField(max_length=200)
