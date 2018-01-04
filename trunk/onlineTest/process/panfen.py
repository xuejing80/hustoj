# _*_ coding:UTF-8 _*_
'''
    包含将C语言源代码标准化函数 standardisation，
    分句函数 fenju，判分函数 panfen

'''
import pymysql


def standardisation(text): #标准化
    
    """
    1、参数text：传入需要标准化的程序
    2、标准化包括但不限于：去注释（两种）、去空格（包括Tab）、处理printf后的内容、统一变量名、函数名等
    
    """
    

    list_text = list(text)               #将程序变成一个个字符的列表，主要为了对换行符\n进行处理，
    for i in range(0,len(list_text)):    #我想通过"\n"进行对程序分句，但仍想保留"\n",因为后面分句还会用到"\n"，
        if list_text[i] == "\n":         #因此将\n转化为一个不会用到的符号串，如我随便输入的下面用到的"\n@&"
            list_text[i] = "\n@&"        #而"@&"相当于是"\n"的一个复制
    text = "".join(list_text)
            
    text = text.split("@&")              #再通过相当于"\n"的复制"@&",来进行分句，此时去掉了"@&",留下了"\n"，还分完了句
    lines = []                           #开始处理"//"后的注释，因为是行注释，所以取每一行，处理完保存在本列表lines[]中（记录所有处理完的行）
    for line in text:                    #取出文本每一行
        for i in range(0,len(line)):
            if i + 1 < len(line) - 1:       
                if line[i] == '/' and line[i + 1] == '/':    #标准化1：进行字符串操作，去掉//后的注释            
                    line = line[0:i]
        lines.append(line)               #将处理完的行line加入列表lines

    str1 = "".join(lines)                #将这些行重新组成一个字符串
                                         #开始处理/**/注释
    head_zhushi = []                     #记录注释头部位置
    end_zhushi = []                      #记录注释尾部位置


    for i in range(0, len(str1)):        #标准化3:去掉/* */中的注释, 循环注释可能会有问题就是这样的/*/*...*/*/的，不过应该没人会这么干
        if i + 1 < len(str1) - 1:
            if str1[i] == '/' and str1[i + 1] == '*':    #记录/*（头）的位置
                head_zhushi.append(i)

            if str1[i] == '*' and str1[i + 1] == '/':    #记录*/（尾）的位置
                end_zhushi.append(i+1)


    list_str1 = list(str1)               #将字符串按每个字符转成列表 ，忘记当初写得时候为什么一会儿转列表一会儿转字符串
    for i in range(0,min(len(head_zhushi),len(end_zhushi))):  #总之这段功能是把/* */中内容删除
        for zf in range(head_zhushi[i],end_zhushi[i] + 1):
            list_str1[zf] = ' '          

            
    
    for i in range(0,len(list_str1)):    #给每个符号前加空格为统一函数名变量名做基础
        if list_str1[i] == ';':          #因为符号贴在变量名、保留字等上面时会影响到这些变量名、保留字的识别  
            list_str1[i] = ' ; '         #因此在符号前后加上空格，使符号能被识别
        elif list_str1[i] == '\n':  
            list_str1[i] = ' \n '
        elif list_str1[i] == '\t':  
            list_str1[i] =  ' '          #'\t'这种对程序逻辑不影响的符号直接就把它去除了
        elif list_str1[i] == '\r':       #还有'\r'
            list_str1[i] = ' '            
        elif list_str1[i] == ',':
            list_str1[i] = ' , '
        elif list_str1[i] == '(':
            list_str1[i] =  ' ( '
        elif list_str1[i] == ')':
            list_str1[i] = ' ) '
        elif list_str1[i] == "=":
            list_str1[i] = ' = '
        elif list_str1[i] == "+":
            list_str1[i] = ' + '
        elif list_str1[i] == "-":
            list_str1[i] = ' - '
        elif list_str1[i] == "*":
            list_str1[i] = ' * '
        elif list_str1[i] == "/":
            list_str1[i] = ' / '
        elif list_str1[i] == "[":
            list_str1[i] = ' [ '
        elif list_str1[i] == "]":
            list_str1[i] = ' ] '
        elif list_str1[i] == "{":
            list_str1[i] = ' { '
        elif list_str1[i] == "}":
            list_str1[i] = ' } '
        if list_str1[i] == '!':             
            list_str1[i] = ' ! '
        elif list_str1[i] == '~':
            list_str1[i] = ' ~ '
        elif list_str1[i] == '&':
            list_str1[i] = ' & '
        elif list_str1[i] == '%':
            list_str1[i] =  ' % '
        elif list_str1[i] == '>':
            list_str1[i] = ' > '
        elif list_str1[i] == "<":
            list_str1[i] = ' < '
        elif list_str1[i] == "^":
            list_str1[i] = ' ^ '
        elif list_str1[i] == "|":
            list_str1[i] = ' | '
        elif list_str1[i] == "?":
            list_str1[i] = ' ? '
        elif list_str1[i] == ":":
            list_str1[i] = ' : '
        elif list_str1[i] == '\"':  
            list_str1[i] = ' \" '


       
    str1 = "".join(list_str1)             #上面步骤处理完后，重新将list_str1[]组成一个字符串
    str1 = str1.replace("    "," ").replace("   "," ").replace("  "," ") #去掉一些多余的空格


    list2_str1 = str1.split(' ')          #将str1按空格分开组成列表

    
    for i in range(0,len(list2_str1)):    #标准化4:将short、long转化为int，float转化为double

        if list2_str1[i] == 'long' or list2_str1[i] == 'short':

            if i + 1 < len(list2_str1) - 1:
                if list2_str1[i+1] == "int":
                    list2_str1[i] = ""
                elif list2_str1[i+1] != "int":
                    list2_str1[i] = "int"

        elif list2_str1[i] == 'float':
            list2_str1[i] = 'double'



    i = 0
    while i < len(list2_str1):
        
        if list2_str1[i] == "printf":                 #标准化：处理printf后的内容

            for j in range(i+1,len(list2_str1)):

                if list2_str1[j] == "\"":             #去除掉printf括号中双引号的部分，这便是程序遇到前一个引号，开始处理

                    list2_str1[j] = " "
                    for x in range(j+1,len(list2_str1)):
                        if list2_str1[x] != "\"":     #当不是下一个引号时删除
                            list2_str1[x] = " " 
                        else:                         #遇到下一个引号结束引号处理
                            list2_str1[x] = " "
                            break
                        
                elif list2_str1[j] == ";":            #遇到分号结束printf处理
                    i = j
                    break
        i = i + 1
            
        
    
    item_num = 0      #变量名序号，可能要改，使全部变量名相同
    hanshu_num = 0    #函数序号
    bianliang = {}    #变量名字典
    hanshu = {}       #函数名字典


    i = 0                       #开始处理函数名、变量名
    """
    接下来的函数名、变量名的处理逻辑：
    遇到int、double、void、char、bool等开始处理
    如果之后一位不是"("或")",则排除当前是强制转换的可能，继续处理；否则当前为强制转换，对之后不做处理
    若排除强制转换，则继续对之后处理
    这一部分我可能会有些地方考虑不周，还需进一步改进
    """
    while i < len(list2_str1):  #函数定义、变量定义、参数定义

        jicun = []              #用来寄存 （int、double） 等关键字后面的 直到 （分号；）或（函数定义前大括号"{"）这段间前的所有字符，例如①int a=3;(则寄存的内容为a=3;) ②int func(int a){...}( 则寄存的内容为func(int a) )
        #pr_jicun = []
            
        if list2_str1[i] == "int" or list2_str1[i] == "double" or list2_str1[i] == "void" or list2_str1[i] == "char" or list2_str1[i] == "bool": #如果碰到这些关键字，则直接继续处理

            if (i+1<len(list2_str1)) and (list2_str1[i+1] != "(" and list2_str1[i+1] != ")"): #当前if条件说明不是强制转换，未写与之配对的else,未对强制转换做处理

                for j in range(i+1,len(list2_str1)):              #排除了强制转换，继续

                    if list2_str1[j] == "(":                      #再后若有"(",则可能是以下这几种情况①int func () 即函数定义 ②int a = (2+3)*4 即变量定义同时有带括号的赋值
                        jicun.append(list2_str1[j])
                        if "=" not in jicun:                          #在jicun中没有“=”，说明上一个注释中的②不成立，说明不是赋值语句，而是函数定义，结束当前这个for循环，进行下一步处理
                            i = j                                 #将表示将要处理位置的i移到当前处理位置j,之后从j再开始处理
                            break
                        else:                                     #否则说明是变量定义，则继续处理直到遇到分号
                            continue

                    elif list2_str1[j] == ";" :                   #遇到了分号，结束这轮处理，带着jicun进入下一个处理环节
                        jicun.append(list2_str1[j])
                        i = j                                     #同上i=j的功能
                        break
                    
                    elif list2_str1[j] == "{" :                   #再后若有"{"，则可能是以下这几种情况①int func(){...} 即可能是函数定义结构开头的"{" ② int a[5] = {1,2,3} 即也可能是数组定义的赋值中的"{" ③函数块开头，如if循环、for循环，循环体的开头会用到"{",但如果没用不知是否会出bug
                        if "[" not in jicun:                        #在jicun中没有"["说明不是数组赋值，而是函数定义结构的开头（即①这种情况），结束这轮处理，带着jicun进入下一个处理环节
                            jicun.append(list2_str1[j])
                            i = j
                            break
                        else:                                       #有"["说明是数组赋值，但也可能是函数首部含有数组参数，即可能是如下情况 ①int a[5] = {1,2,3} ②int func (int a[5]){
                            if "=" in jicun:                        #有"="说明是数组赋值,因为c语言在函数定义时中无法直接为数组参数赋值
                                jicun.append(list2_str1[j])
                            else:                                   #否则为包含数组参数的函数,为下一步做区分，不把"{"加入
                                pass

                        if list2_str1[j-1] == ")" or list2_str1[j-1] == "\n":#"{"前是")"或"\n",则为函数定义或函数块开头，则结束当前处理,（"\n"在这里可能是个bug, 但为了之后分句需要保留"\n"）
                            i = j
                            break
                            
                    else:                                       #不是以上情况，则将该字符加入jicun列表，继续这个for循环
                        jicun.append(list2_str1[j])


            #上一个步骤处理完，开始对jicun做处理
            if "(" in jicun and "{"  not in jicun and ";" not in jicun and "=" not in jicun:   #这种情况下寄存的为函数名,如int func ()中的func
                    
                for n in jicun:
                    if n != "(":                                #将函数名加入函数名字典，为之后整个程序调用到此函数的函数名做替换
                        hanshu[n] = "hanshu" + str(hanshu_num)
                        hanshu_num = hanshu_num + 1
                        
                    else:
                        break
           

            elif (";" in jicun) or ( "(" not in jicun and "{" in jicun and ";" not in jicun ) or ("["in jicun and ")"in jicun):    #此时寄存了变量或函数参数，我们要提取其中的变量名来加入变量名字典

                if "[" not in jicun:                   #不存在数组
                    k = 0
                    jicun2 = []                        #保存可能是变量的字符

                    while k < len(jicun):     
                        
                        if jicun[k] != "=" :           #因为此时寄存的是变量或函数参数，它们有可能会有赋值，所以取出赋值符号"="前的内容，加入jicun2,等jicun2继续处理

                            jicun2.append(jicun[k])

                        else:                          #遇到了"=",说明存在赋值，但还存在这样一种情况 int a=10,b; 即定义了一个变量并赋值后，后面还定义了其他变量，我们要继续将后面可能是变量的符号加入jicun2
                            for x in range( k+1,len(jicun) ):
                                if jicun[x] != "," and jicun[x] != ";":
                                    continue
                                
                                else: 
                                    k = x
                                    break
                                
                        k = k + 1
                        
                                                      #对处理jicun后得到的jicun2继续处理
                    for k in range(0,len(jicun2)):
                            
                        if jicun2[k] != 'int' and jicun2[k] != 'double' and jicun2[k] != 'void' and jicun2[k] != 'char' and jicun2[k] != 'bool'and jicun2[k] != "," and jicun2[k] != ";" and jicun2[k] != "*" and jicun2[k] != "&" and jicun2[k] != " " and jicun2[k] != ")"and jicun2[k] != "\n":

                                                      #jicun2中可能会存在上面一句if中提到的这些奇怪的东西，而这些都不是变量名或参数名，而其余的的就是了
                            bianliang[jicun2[k]] = "item" + str(item_num)                           
                            item_num = item_num + 1  #将变量名加入变量名字典，为之后整个程序使用的此变量做替换
                            


                else:                                #存在数组
                    k = 0
                    jicun2 = []                      #保存可能是变量的字符
                    sign = 0                         #标记是否存在数组赋值

                    while k < len(jicun):                    

                        if jicun[k] != "=" and jicun[k] != "[" :    #把遇到"=","["前的东西都保存下来

                            jicun2.append(jicun[k])

                        elif jicun[k] == "=":                       #遇到了"="，和上一步中遇到"="一样处理

                            for x in range( k+1,len(jicun) ):
                                if jicun[x] != "," and jicun[x] != ";":
                                    continue
                                
                                else: 
                                    k = x
                                    break
                                
                        elif jicun[k] == "[":                       #遇到"[",即存在数组，分为有赋值和没赋值两种情况

                            for x in range( k+1,len(jicun) ):       #遍历jicun,存在"{"符号说明有赋值 （有bug吗、感觉有点怪怪的）
                                if jicun[x] == "{":
                                    sign = 1                        #将sign置为1，表示存在数组赋值
                                    

                            if sign == 0:                           #不存在数组赋值
                                for x in range( k+1,len(jicun) ):   #将处理位置指到"]"上， 如处理int a[10],b; 这时我们只需要a和b两个变量名，中间的[10],是没用的
                                    if jicun[x] != "]" :
                                        continue
                                    
                                    else: 
                                        k = x
                                        break
                                    
                            elif sign == 1:                         #存在数组赋值
                                for x in range( k+1,len(jicun) ):   #将处理位置指到"}"上， 如处理int a[10]={1,2,3},b; 这时我们只需要a和b两个变量名，中间的[10]={1,2,3},是没用的
                                    if jicun[x] != "}":
                                        continue

                                    else:
                                        k = x + 1
                                        break
                                
                        k = k + 1


                    for k in range(0,len(jicun2)):
                            
                        if jicun2[k] != 'int' and jicun2[k] != 'double' and jicun2[k] != 'void' and jicun2[k] != 'char' and jicun2[k] != 'bool'and jicun2[k] != "," and jicun2[k] != ";" and jicun2[k] != "*" and jicun2[k] != "&" and jicun2[k] != " " and jicun2[k] != ")"and jicun2[k] != "\n":
                                                                    #这一步和上面的一个意思
                            bianliang[jicun2[k]] = "item" + str(item_num)
                            
                            item_num = item_num + 1         
        
        i = i + 1

    for i in range(0,len(list2_str1)):                            #函数、变量名替换
        if list2_str1[i] in bianliang:
            list2_str1[i] = bianliang[list2_str1[i]]

        elif list2_str1[i] in hanshu:
            list2_str1[i] = hanshu[list2_str1[i]]



    str1 = "".join(list2_str1)         #将list2_str1[]再重组成一个字符串          


    j = 0
    str2 = []
    for i in str1:
 
        if i != " ":                   #标准化6：去空格去换行符
            str2.append(str1[j])
            
        j = j + 1    
    
    str2 = "".join(str2)

    str2 = str2.lower()               #标准化2：大写转小写

    return str2


def fenju(str2):
    """
    分句基本思路是按分号;处理
    但也应考虑一些其他情况，如预处理、换行，函数段等
    """

    i = 0
    fenju = []                             #保存分句
        
    while i < len(str2):

        ju = []                            #保存形成一句的各个符号

        if str2[i] == "#":                 #遇见"#",本句为预处理语句

            for j in range(i,len(str2)):

                if str2[j] != "\n":        #在遇到"\n"前全部保存下来
                    ju.append(str2[j])
                else:                      
                    ju.append(str2[j])
                    i = j                  #将处理位置指到j
                    fenju.append("".join(ju)) #将ju中的符号组成一整句，保存到fenju列表中
                    break
                
        elif str2[i] == "{":               #遇到"{",通常是新的一句的开始，处理到";"为止，这边也可能需要改进，因为"{"后可能会有很多其他情况
            for j in range(i+1,len(str2)):
                if str2[j] != ";":
                    ju.append(str2[j])
                else:
                    ju.append(str2[j])
                    i = j
                    fenju.append("".join(ju))
                    break
                
        elif str2[i] == "\n":             #不保存"\n",即把"\n"删掉
            pass
            
        else:                             #其他就按照分号与分号间为一句 或 分号与大括号之间为一句
            for j in range(i,len(str2)):
                if str2[j] == ";":
                    ju.append(str2[j])
                    i = j
                    fenju.append("".join(ju))
                    break                     
                elif str2[j] == ")" and j+2 < len(str2):
                    if str2[j+1] == "{" or (str2[j+1] == "\n" and str2[j+2] == "{"):
                        ju.append(str2[j])
                        i = j
                        fenju.append("".join(ju))                    
                        break
                else:
                    ju.append(str2[j])          
        
        i = i + 1

    
    fenju2 = []
    for i in fenju:
        list_i = list(i)
        for j in range(0,len(list_i)):
            if list_i[j] == "\n" or list_i[j] == "(" or list_i[j] == ")" or list_i[j] == "{" or list_i[j] == "}":  #去除这些符号
                list_i[j] = ""
        i = "".join(list_i)
        fenju2.append(i)

    fenju2 = list(set(fenju2))              #去除相同元素        
    return fenju2


# 将源代码进行标准化、分句处理
def get_token(code):
    token = fenju(standardisation(code))
    return token

# 将标准化、分句完成的代码进行先死度判分
def panfen(str3,STR3):
    if len(str3) == 0:
        return 0 
    sum_1 = str3 + STR3
    sum_2 = list(set(sum_1))                #去除相同元素
    return (len(sum_1) - len(sum_2))*1.0/len(str3)

# 得到两段代码的相似度
def get_similarity(code_1 ,code_2):
    result1 = fenju(standardisation(code_1))
    result2 = fenju(standardisation(code_2))
    exponent = panfen(result1, result2)
    return exponent

 
