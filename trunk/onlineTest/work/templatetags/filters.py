from django import template
register = template.Library()

@register.filter
def myFilter(value):
    tempstr = value
    tempstr = tempstr.replace("<","&lt;")
    tempstr = tempstr.replace(">","&gt;")
    tempstr = tempstr.replace(" ","&nbsp;")
    tempstr = tempstr.replace("&lt;sup&gt;","<sup>")
    tempstr = tempstr.replace("&lt;/sup&gt;","</sup>")
    tempstr = tempstr.replace("&lt;sub&gt;","<sub>")
    tempstr = tempstr.replace("&lt;/sub&gt;","</sub>")
    tempstr = tempstr.replace("&lt;pre&gt;","<pre>")
    tempstr = tempstr.replace("&lt;/pre&gt;","</pre>")
    tempstr = tempstr.replace("</pre>\r\n","</pre>")
    tempstr = tempstr.replace("|||"," 或者 ") # 填空题答案过滤器
    return tempstr