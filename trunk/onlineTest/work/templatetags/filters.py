from django import template
import re
register = template.Library()

@register.filter
def myFilter(value):
    tempstr = value
    tempstr = tempstr.replace("<","&lt;")
    tempstr = tempstr.replace(">","&gt;")
    tempstr = tempstr.replace(" ","&nbsp;")
    pattern = '&lt;img&nbsp;alt="(?P<alt>.+?)"&nbsp;src="(?P<src>.+?)"&nbsp;width="(?P<width>\d+?)"&nbsp;height="(?P<height>\d+?)"&gt;'
    ls = re.findall(pattern, tempstr)
    for i in range(len(ls)):
        newString = '<img alt="'+ls[i][0]+'" src="'+ls[i][1]+'" width="'+ls[i][2]+'" height="'+ls[i][3]+'">'
        tempstr = re.sub(pattern, newString, tempstr, count=1)
    tempstr = tempstr.replace("&lt;br&gt;","<br>")
    tempstr = tempstr.replace("&lt;p&gt;","<p>")
    tempstr = tempstr.replace("&lt;/p&gt;","</p>")
    tempstr = tempstr.replace("&lt;sup&gt;","<sup>")
    tempstr = tempstr.replace("&lt;/sup&gt;","</sup>")
    tempstr = tempstr.replace("&lt;sub&gt;","<sub>")
    tempstr = tempstr.replace("&lt;/sub&gt;","</sub>")
    tempstr = tempstr.replace("&lt;pre&gt;","<pre>")
    tempstr = tempstr.replace("&lt;/pre&gt;","</pre>")
    tempstr = tempstr.replace("</pre>\r\n","</pre>")
    tempstr = tempstr.replace("&lt;code&gt;","<code>")
    tempstr = tempstr.replace("&lt;/code&gt;","</code>")
    tempstr = tempstr.replace("</code>\r\n","</code>")
    tempstr = tempstr.replace("|||"," 或者 ") # 填空题答案过滤器
    return tempstr

@register.filter
def myDiv(value,total):
        return str("%.2f"%(round((value * 100 / total), 2)))+'%'

@register.filter
def removeScript(value):
    tempstr = value
    tempstr = tempstr.replace("<script>","")
    tempstr = tempstr.replace("</script>","")
    return tempstr

@register.filter
def get_range(value):
    return range(1,value)
