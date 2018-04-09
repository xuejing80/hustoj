import pymysql
pymysql.install_as_MySQLdb()

import os
if not os.path.exists("allCode"):
    os.mkdir("allCode")
if not os.path.exists("codeWeekTarFiles"):
    os.mkdir("codeWeekTarFiles")
if not os.path.exists("codeZip"):
    os.mkdir("codeZip")
if not os.path.exists("reportFile"):
    os.mkdir("reportFile")
if not os.path.exists("upload"):
    os.mkdir("upload")