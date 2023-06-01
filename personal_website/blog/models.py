from django.db import models
from project.models import Project

# Create your models here.


class Blog(models.Model):
    author_id = models.IntegerField()
    blog_id = models.IntegerField()
    title = models.CharField(max_length=200)
    pub_date = models.DateTimeField("data published")
    content = models.CharField(max_length=5000)
    priority = models.IntegerField()

    def __str__(self):
        return f"[{self.blog_id}]{self.title}"
