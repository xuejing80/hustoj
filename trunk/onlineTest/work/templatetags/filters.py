from django import template
register = template.Library()

@register.filter
def myFilter(value):
    tempstr = value
    tempstr = tempstr.replace("<<","&lt;&lt;")
    tempstr = tempstr.replace(">>","&gt;&gt;")
    return tempstr
