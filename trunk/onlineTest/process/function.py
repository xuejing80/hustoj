import pymysql
from process.panfen import get_similarity, get_token, panfen
import time


# 建立mysql连接
conn = pymysql.connect(host="localhost", port=3306, 
                    user="root", passwd="qwer1234", db="jol")

cur = conn.cursor()

# 输入id，得到相似度得分
def get_similarity(id):
    # 根据 solution_id 查询对应的 source_code
    # 结果保存到 result 中
    query = "SELECT source FROM source_code WHERE solution_id=%s"
    query1 = "SELECT problem_id FROM solution WHERE solution_id=%s"
    try:
        n_rows = cur.execute(query, id)
        result = cur.fetchall()[0][0]
    except:
        return 0
    if len(result)==3:
        return 0
    print(result)
    print(len(result))
    if len(result)==0:
        return 0
    n_rows = cur.execute(query1, id)
    problem_id = cur.fetchall()[0][0]
    token = get_token(result)
    query2 = "SELECT tokens FROM true_code WHERE problem=%s"
    n_rows = cur.execute(query2, problem_id)
    true_tokens = cur.fetchall()

    final_exponent = 0
    for true_token in true_tokens:
        exponent = panfen(true_token[0].split(','), token)
        if(exponent > final_exponent and exponent<=0.8):
            final_exponent = exponent
    
    return final_exponent

def addTrueAnswer(id):
    query = "SELECT source FROM source_code WHERE solution_id=%s"
    query1 = "SELECT problem_id FROM solution WHERE solution_id=%s"
    query2 = "INSERT INTO true_code VALUES(%s, %s)"
    if get_similarity(id) < 0.8:
        try:
            n_rows = cur.execute(query, id)
            result = cur.fetchall()[0][0]
            tokens = get_token(result)
        except:
            pass
        try:
            n_rows = cur.execute(query1, id)
            problem_id = cur.fetchall()[0][0]
        except:
            pass
        try:
            cur.execute(query2, (problem_id, ','.join(tokens)))
        except:
            pass

        
        








