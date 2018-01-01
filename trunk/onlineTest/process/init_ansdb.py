'''
    构建C语言编程题的正确答案库
'''
import pymysql
from panfen import get_similarity, get_token, panfen
import time


# 建立mysql连接
conn = pymysql.connect(host="localhost", port=3306, 
                    user="root", passwd="qwer1234", db="jol")
cur = conn.cursor()


# 建立正确答案库 true_code
query0 = "CREATE TABLE true_code (problem INT, tokens LONGTEXT)"
try:
    n_rows = cur.execute(query0)
    conn.commit()
except:
    pass



# 查询正确的编程题答案的solution_id, 保存到result中
time1 = time.time()
query = "SELECT solution_id, problem_id FROM solution WHERE result=4 AND language=0"
n_rows = cur.execute(query)
results = list(cur.fetchall())
time2 = time.time()
print("共"+str(len(results))+"条正确答案")
print("查询所花时间：" + str((time2-time1)) + "秒")


# 建立 列表true_codes 用于保存正确答案
# 将正确答案的 source_code 进行分句处理,以元组的形式保存到 true_codes 中
true_codes = []
time1 = time.time()
query1 = "SELECT source FROM source_code WHERE solution_id=%s"
for i in range(0, len(results)):
    n_rows = cur.execute(query1, results[i][0])
    code = cur.fetchall()[0][0]
    true_codes.append((str(results[i][1]), get_token(code)))
    print("已标准化处理了" + str(i) + "条答案,共" + str(len(results)) + "条")
time2 = time.time()
print("标准化分句用时" + str((time2-time1)) + "秒")
true_codes.sort()


# 判断代码和正确代码库中代码的相似度
# 相似度超过80%，则返回 False
def judge(answers, code):
    flag = True
    for ans in answers:
        if(ans[0]==code[0] and panfen(code[1],ans[1]) >= 0.8) == True:
            flag = False
            break
    return flag


# 处理数据并存入数据库
ansdb = []
query2 = "INSERT INTO true_code VALUES(%s, %s)"
start_time = time.time()
for index in range(0,len(true_codes)):
    time1 = time.time()
    ''' 
        本条答案与答案库中的答案，
        相似度小于80%则插入答案库，否则放弃
     '''
    if judge(ansdb, true_codes[index]):
        ansdb.append(true_codes[index])
        cur.execute(query2, (true_codes[index][0], ','.join((true_codes[index][1])) ))
        conn.commit()
    print("已插入" + str(index) + "条答案,共" + str(len(results)) + "条")
end_time = time.time()    
print("构建答案库耗时" + str(end_time-start_time) + "s")    


    




