# 2018-4-24
# 传入homework_id，返回可疑抄袭同学的分组(字典形式)
# 考虑数据可视化，将分组信息制成饼图

# encoding: utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from judge.models import Solution, SourceCode
from work.models import HomeworkAnswer, MyHomework
from process.views import get_similarity_v2

def getCopyGroups(homework_id,studentids):
    copyGroups = dict()
    homework = MyHomework.objects.filter(id=homework_id).first()
    if homework is None:
        return copyGroups
    homework_answers = homework.homeworkanswer_set.all().filter(creator_id__in = studentids)
    finished_students  = []
    isPlaced = []
    for homework_answer in homework_answers:
        finished_students.append(str(homework_answer.creator.id_num)+str(homework_answer.creator.username))
        isPlaced.append(0)
    try:
        problem_ids = list(map(int,homework.problem_ids.split(",")))
    except:
        problem_ids = []
    if problem_ids:
        for i in range(len(homework_answers)):
            my_homework_answer = homework_answers[i]
            for j in range(i+1, len(homework_answers)):
                if isPlaced[j] == 1:
                    continue
                flag = 1
                for pid in problem_ids:
                    try:
                        solution = Solution.objects.get(problem_id=pid,homework_answer=my_homework_answer)
                        try:
                            sourceCode = SourceCode.objects.get(solution_id=solution.solution_id).source
                        except ObjectDoesNotExist:
                            sourceCode = "代码未找到"
                        solution_compare = Solution.objects.get(problem_id=pid, homework_answer=homework_answers[j])
                        try:
                            sourceCode_compare = SourceCode.objects.get(solution_id=solution_compare.solution_id).source
                        except ObjectDoesNotExist:
                            sourceCode_compare = "用于比较的代码未找到"
                        if get_similarity_v2(sourceCode,sourceCode_compare) < 0.8:
                            flag = 0
                            break
                    except:
                        pass
                if flag == 1 and isPlaced[j] == 0:
                    try:
                        copyGroups[finished_students[i]] += " " + finished_students[j]
                    except:
                        copyGroups[finished_students[i]] = finished_students[j]
                    isPlaced[j] = 1
    return copyGroups
