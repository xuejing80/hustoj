from django.shortcuts import render
from django.contrib.auth.models import Group
from django.db.models import Count
from .models import Census, Weights
from auth_system.models import MyUser
from judge.models import ChoiceProblem, DuchengProblem, Problem, ClassName
from django.utils import timezone
from django.db.models import Sum
import datetime
# Create your views here.

def Record():
    registered_users =  len(MyUser.objects.annotate(Count('Number_user')))
    choices = len(ChoiceProblem.objects.annotate(Count('id')))
    programms = len(Problem.objects.annotate(Count('problem_id')))
    fills = len(DuchengProblem.objects.annotate(Count('ducheng_id')))
    save_time = timezone.now().date()
    record = Census(registered_users=registered_users, choices=choices, programms=programms, fills=fills, save_time=save_time)
    record.save()

def Nums(A):
    today = timezone.now().date()
    sta = []
    for i in range(7, 0, -1):
        date = today - datetime.timedelta(days=i)
        temp = Census.objects.filter(save_time=date).aggregate(sum=Sum(A))
        nums = temp['sum'] or 0
        sta.append(nums)
    return sta
 
def Dates():
    today = timezone.now().date()
    dates = []
    for i in range(7, 0, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
    return dates
