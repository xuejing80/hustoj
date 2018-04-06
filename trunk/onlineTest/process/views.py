from django.shortcuts import render
from judge.models import  Solution,SourceCode
from process.panfen import get_token, panfen
from process.models import Ansdb
import json
from difflib import *
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
                tokens = tokens,
                solution_id = solu_id
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
            tokens = json.dumps(tokens)
        )
        ans.save()

# 比较Yuan、ratio、quick_ratio、real_quick_ratio
def test():
    right_solution = Solution.objects.filter(language=0, result=4, problem_id=8)[0]
    first_column = []
    second_column = []
    third_column = []
    fourth_column = []
    sequenceMatcher = SequenceMatcher()
    right_solution_code = SourceCode.objects.filter(solution_id=right_solution.solution_id)[0].source
    right_solution_tokens = get_token(right_solution_code)
    solutions = Solution.objects.filter(language=0, result=4,problem_id=8)
    total = len(solutions)
    for i in range(0, total):
        solution = solutions[i]
        solu_id = solution.solution_id
        if judge_insert(solu_id) == True:
            source = SourceCode.objects.filter(solution_id=solu_id)[0].source
            compare_tokens = json.dumps(get_token(source))
            first_column.append(panfen(right_solution_tokens, json.loads(compare_tokens)))
            sequenceMatcher.set_seqs(source,right_solution_code)
            second_column.append(sequenceMatcher.ratio())
            third_column.append(sequenceMatcher.quick_ratio())
            fourth_column.append(sequenceMatcher.real_quick_ratio())
    file = open('Yuan.txt','w')
    file.write(str(first_column))
    file.close()
    file = open('ratio.txt', 'w')
    file.write(str(second_column))
    file.close()
    file = open('quick_ratio.txt', 'w')
    file.write(str(third_column))
    file.close()
    file = open('real_quick_ratio.txt', 'w')
    file.write(str(fourth_column))
    file.close()

def get_similarity_v2(sourceCode, sourceCode_comapre):
    '''
    :param sourceCode:该同学该题的代码
    :param sourceCode_comapre:用来比较的代码,来源为同样提交该作业的其他同学
    :return:返回相似度
    '''
    tokens = get_token(sourceCode)
    tokens_compare = get_token(sourceCode_comapre)
    exponent = panfen(tokens, tokens_compare)
    return exponent
