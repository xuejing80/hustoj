from work.models import MyHomework
from django.core.exceptions import ObjectDoesNotExist

for i  in MyHomework.objects.all():
    print(str(i.id) +"   "+ str(i.finished_students.count()) +"   " + str(i.homeworkanswer_set.filter().count())) 
