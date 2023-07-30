from django.contrib import admin

# Register your models here.


from .models import Project, User, Purchase, ProjectTag, Order


class TagInline(admin.StackedInline):
    model = ProjectTag
    extra = 0


class ProjectAdmin(admin.ModelAdmin):
    inlines = [TagInline]


admin.site.register(Project, ProjectAdmin)
admin.site.register(User)
admin.site.register(Purchase)
admin.site.register(ProjectTag)
admin.site.register(Order)
