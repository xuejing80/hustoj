from work.models import MyHomework, HomeworkAnswer
from work.views import judge_homework
import _thread

for i in HomeworkAnswer.objects.all():
    if i.score and i.score != i.homework.total_score:
        for j in i.solution_set.all():
            if j.result in [0, 1, 2, 3]:
                j.result = 0
                j.save()
        judge_homework(i)
        print('judged ' + str(i.id))

from work.models import MyHomework, HomeworkAnswer

homework = MyHomework.objects.get(pk=175)
for i in homework.homeworkanswer_set.all():
    for j in i.solution_set.all():
        judge_homework(i)
        print('judged' + str(j.pk))

from work.models import MyHomework
import json

for i in MyHomework.objects.all():
    try:
        for info in json.loads(i.problem_info):
            try:
                for case in info['testcases']:  # 获取题目的测试分数
                    if case['desc']:
                        pass
            except Exception as e:
                print("error on get problem score :" + str(i.pk) + str(e))
    except:
        print("error encode " + str(i.pk))
