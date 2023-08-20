from django import template

register = template.Library()

@register.filter
def addstr(arg1, arg2):
    return str(arg1) + str(arg2)

@register.filter
def div(arg1, arg2):
    return float(arg1) / float(arg2)

@register.filter
def mul(arg1, arg2):
    return int(float(arg1) * float(arg2))
