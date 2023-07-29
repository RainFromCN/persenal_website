from django.db import models

from project.models import User

# # Create your models here.
# class Request(models.Model):
#     publisher = models.ForeignKey(to=User, on_delete=models.CASCADE)  # 发布者
#     title = models.CharField(max_length=50)  # 需求的标题
#     content = models.CharField()  # 需求内容
#     commission = models.IntegerField()  # 需求佣金

#     # 状态
#     hits = models.IntegerField(default=0)  # 该需求的点击量
#     state = models.IntegerField(choices=[0,1])  # 该需求的状态，0代表尚未解决，1代表已经解决
