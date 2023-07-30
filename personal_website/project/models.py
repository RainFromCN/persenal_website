from django.db import models


# Create your models here.
class Project(models.Model):
    # 项目的基本信息
    prj_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    brief = models.CharField(max_length=1000, default='')
    price = models.FloatField(default=9.9)

    # 当前项目的简介，论文以及教程
    introduction = models.TextField(default='introduction')
    tutorial = models.TextField(default='tutorial')

    def __str__(self):
        return f"[{self.prj_id}]{self.name}"


class ProjectTag(models.Model):
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.text}"


class User(models.Model):
    # 用户基本信息
    user_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    login_times = models.IntegerField(default=0)  # 累计登录次数

    # 其他信息
    introduction = models.CharField(max_length=100, default='')  # 个人简介

    def __str__(self):
        return f"[{self.user_id}]{self.name}"
    

class ProjectComment(models.Model):
    """项目评价"""
    text = models.CharField(max_length=500)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.date} @{self.user}'
    

class ProjectQuestion(models.Model):
    """项目问大家"""
    text = models.CharField(max_length=200)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.date} @{self.user}'
    

class ProjectAnswer(models.Model):
    """项目问大家回答问题"""
    text = models.CharField(max_length=200)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    question = models.ForeignKey(to=ProjectQuestion, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.date} @{self.user}'
  

class Order(models.Model):
    order_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.order_id}"


class Purchase(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.DO_NOTHING)
    project = models.ForeignKey(to=Project, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"[{self.order.order_id}] @{self.user.name}"
