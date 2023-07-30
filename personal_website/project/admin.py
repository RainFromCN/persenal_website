from django.contrib import admin

# Register your models here.


from .models import (
    Project, 
    User, 
    Purchase, 
    ProjectTag, 
    Order,
    ProjectComment,
)


class ProjectTagInline(admin.StackedInline):
    model = ProjectTag
    extra = 0


class ProjectCommentInline(admin.StackedInline):
    model = ProjectComment
    extra = 0


class ProjectAdmin(admin.ModelAdmin):
    inlines = [
        ProjectTagInline, 
        ProjectCommentInline
    ]


admin.site.register(Project, ProjectAdmin)
admin.site.register(User)
admin.site.register(Purchase)
admin.site.register(Order)
