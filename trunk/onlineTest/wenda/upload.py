#-*-coding:utf8-*-

from django.conf import settings
from django.http import HttpResponse
import os
import json
import string
import random
from wenda.models import UploadInfo
from django.db.models import Sum

# {
#   "success": true/false,
#   "msg": "error message", # optional
#   "file_path": "[real file path]"
# }

def generateId(size=16, chars=string.ascii_letters + string.digits):
	    return ''.join(random.choice(chars) for _ in range(size))

def generateDir(dirName):
    dirName = os.path.join(settings.MEDIA_ROOT , dirName)
    if not os.path.exists(dirName):
        # print(dirName)
        os.makedirs(dirName)
    return dirName

def imageUpload(request, dirName):
    image = request.FILES.get("img", None)
    name = request.POST.get("original_filename", None)
    uid = request.user.id
    if image is None:
        msg = {"success":False,"msg":"照片为空"}
    elif name is None:
        msg = {"success":False,"msg":"照片名为空"}
    else:
        allowSuffix = ['jpg','png','jepg']
        fileSuffix = name.split('.')[-1]
        # 用户已用空间 单位kb
        user_space = UploadInfo.objects.filter(uid=uid).aggregate(Sum('file_size'))['file_size__sum']
        # print(user_space)
        # 规定每个用户只有20Mb的上传空间
        if (user_space is not None) and user_space > 1024 * 20:
            msg = {"success":False,"msg":"空间有限无法上传"}
            # 照片大小不能大于4Mb
            # print(image.size)
        elif image.size > 1024 * 1024 * 4:
            msg = {"success":False,"msg":"照片太大"}

        elif fileSuffix not in allowSuffix:
            # print(fileSuffix)
            msg = {"success":False,"msg":"照片格式不正确"}
        else:
            fullPtah = generateDir(dirName)
            fileName = generateId() + "_" + str(request.user.id) + '.' +fileSuffix
            filePath = os.path.join(fullPtah,fileName)
            try:
                with open(filePath,'wb') as saveImg:
                    saveImg.write(image.file.read())
                imgUrl = r'/wenda/get_img/'  + dirName + r'/' +fileName
                msg = {"success":True,"file_path":imgUrl}
                ip = request.META['REMOTE_ADDR']
                file_size = int(image.size / 1024)
                UploadInfo.objects.create(uid=uid, ip=ip,file_size=file_size)
            except:
                msg = {"success":False,"msg":"服务繁忙，请稍后重试"}
            
    return HttpResponse(json.dumps(msg), content_type="application/json")

            
