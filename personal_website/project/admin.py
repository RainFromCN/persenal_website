from django.contrib import admin

# Register your models here.


from .models import Project, User, Purchase


admin.site.register(Project)
admin.site.register(User)
admin.site.register(Purchase)
