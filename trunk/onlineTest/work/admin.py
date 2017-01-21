from django.contrib import admin
# Register your models here.
from work.models import HomeWork, HomeworkAnswer, BanJi, MyHomework, TempHomeworkAnswer

class MyhomeworkAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'courser', 'creater')

class Homework_AnswerAdmin(admin.ModelAdmin):
    list_display = ()

admin.site.register(HomeWork)
admin.site.register(HomeworkAnswer)
admin.site.register(BanJi)
admin.site.register(MyHomework, MyhomeworkAdmin)
admin.site.register(TempHomeworkAnswer)
