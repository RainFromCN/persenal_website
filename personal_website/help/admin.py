from django.contrib import admin

# Register your models here.
from .models import (
    Request,
    RequestFollows,
    Cooperation,
    ClientFeedback,
    ServerFeedback,
    CooperationAppealing,
    CooperationPayment,
)


class RequestFollowsInline(admin.StackedInline):
    model = RequestFollows
    extra = 0


class RequestAdmin(admin.ModelAdmin):
    inlines = [
        RequestFollowsInline,
    ]

admin.site.register(Request, RequestAdmin)
admin.site.register(Cooperation)
admin.site.register(CooperationAppealing)
admin.site.register(CooperationPayment)
