from django.shortcuts import render
from django.http import JsonResponse
from faq.models import faqs
from django.core.exceptions import ObjectDoesNotExist
import json,urllib.request,urllib.parse

# Create your views here.

def index(request):
    return render(request, 'faq.html')

def send(request):
    receive = request.POST['q']
    json_data = {}

    try:
        faq = faqs.objects.get(question_content=receive)
    except ObjectDoesNotExist:
        values={
            "key":"880abf7cb9484371bd5ee8fb02d51114",
            "info":receive,
            "userid":"xuejing80"
        }
        url = "http://www.tuling123.com/openapi/api"
        data = urllib.parse.urlencode(values)
        binary_data = bytes(data,'utf8')
        request=urllib.request.Request(url)
        result = urllib.request.urlopen(request,binary_data).read()
        result = str(result, encoding = "utf-8")
        result = json.loads(result)
        json_data['data'] = result['text']
        #json_data['data'] = "对不起，我听不懂你在说什么，我会把你的问题转交给管理员。"
    else:
        json_data['data'] = faq.answer_content
        
    return JsonResponse(json_data)
