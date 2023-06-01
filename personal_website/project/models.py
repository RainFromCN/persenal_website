from django.db import models
from django.utils.timezone import now
import os, sys


DIR = 'D:\develop\personalWeb_ws\persenal_website\projects'


# Create your models here.
class Project(models.Model):
    prj_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    author_id = models.IntegerField()
    pub_date = models.DateTimeField("data published", default=now())

    introduction = models.TextField(max_length=4000, default='introduction')
    paper = models.TextField(max_length=4000, default='paper')
    tutorial = models.TextField(max_length=4000, default='tutorial')
  
    def __str__(self):
        return f"[{self.prj_id}]{self.name}"
