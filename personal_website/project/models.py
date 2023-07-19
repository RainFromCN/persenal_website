from django.db import models
from django.utils.timezone import now


# Create your models here.
class Project(models.Model):
    # 项目的基本信息
    prj_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    brief = models.CharField(max_length=1000, default='')
    pub_date = models.DateTimeField("data published", default=now())
    price = models.FloatField(default=9.9)

    # 当前项目的简介，论文以及教程
    introduction = models.TextField(default='introduction')
    tutorial = models.TextField(default='tutorial')

    def __str__(self):
        return f"[{self.prj_id}]{self.name}"


class User(models.Model):
    # 用户基本信息
    user_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    login_times = models.IntegerField(default=0)  # 累计登录次数

    def __str__(self):
        return f"[{self.user_id}]{self.name}"


class Tag(models.Model):
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.text}"


class Purchase(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.DO_NOTHING)
    project = models.ForeignKey(to=Project, on_delete=models.DO_NOTHING)
    date = models.DateTimeField("purchase date", default=now())

    def __str__(self):
        return f"[{self.date}]: @{self.user.name}"
