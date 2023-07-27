from django.contrib import admin

# Register your models here.


from .models import Project, User, Purchase, Tag, Order


class TagInline(admin.StackedInline):
    model = Tag
    extra = 0


class ProjectAdmin(admin.ModelAdmin):
    inlines = [TagInline]


admin.site.register(Project, ProjectAdmin)
admin.site.register(User)
admin.site.register(Purchase)
admin.site.register(Tag)
admin.site.register(Order)
