from django.db import models


# Create your models here.
class Project(models.Model):
    prj_id = models.IntegerField()
    name = models.CharField(max_length=100)
    pub_date = models.DateTimeField()
    video = models.CharField(max_length=200) # 项目介绍视频
