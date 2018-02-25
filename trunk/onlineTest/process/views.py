from django.shortcuts import render
from judge.models import  Solution,SourceCode
from process.panfen import get_token, panfen
from process.models import Ansdb
import json
# Create your views here.


def init_ansdb():
    ''' 初始化C语言答案库 '''
    solutions = Solution.objects.filter(language=0, result=4)
    total = len(solutions)
    for i in range(0, total):
        solution = solutions[i]
        solu_id = solution.solution_id
        if judge_insert(solu_id)==True:
            source = SourceCode.objects.filter(solution_id = solu_id)[0].source
            tokens = json.dumps(get_token(source))
            ans = Ansdb(
                problem_id = solution.problem_id,
                language = solution.language,
                tokens = tokens
            )
        ans.save() 
        print(str(i) + "/" + str(total)) 

def get_similarity(id):
    ''' 传入参数id表示solution_id，
    返回与正确答案库匹配的相似度 '''
    problem_id = Solution.objects.filter(solution_id=id)[0].problem_id
    source_code = SourceCode.objects.filter(solution_id=id)[0].source
    tokens = get_token(source_code)
    final_exponent = 0
    for true_ans in Ansdb.objects.filter(problem_id = problem_id):
        exponent = panfen(tokens, json.loads(true_ans.tokens))
        if exponent > final_exponent and exponent < 0.8:
            final_exponent = exponent
    return final_exponent

def judge_insert(id):
    ''' 
    传入参数id表示solution_id，
    与正确答案库中答案匹对，
    若相似度超过0.8，则返回Flase，
    否则返回True。
    '''
    problem_id = Solution.objects.filter(solution_id=id)[0].problem_id
    source_code = SourceCode.objects.filter(solution_id=id)[0].source
    tokens = get_token(source_code)
    flag = True
    final_exponent = 0
    for true_ans in Ansdb.objects.filter(problem_id = problem_id):
        exponent = panfen(tokens, json.loads(true_ans.tokens))
        if exponent > 0.8:
            flag = False
            break
    return flag

def update_ansdb(id):
    ''' 更新答案库 '''
    if judge_insert(id):
        solution = Solution.objects.filter(solution_id = id)[0]
        source = SourceCode.objects.filter(solution_id = id)[0].source
        tokens = get_token(source)       
        ans = Ansdb(
            problem_id = solution.problem_id,
            language = solution.language,
            tokens = tokens
        )
        ans.save()

        
    

