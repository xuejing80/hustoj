import pymysql
pymysql.install_as_MySQLdb()

from .settings import USER_FILE_DIR
import os
if not os.path.exists(USER_FILE_DIR)
    os.mkdir(USER_FILE_DIR)
if not os.path.exists(os.path.join(USER_FILE_DIR, "allCode")):
    os.mkdir(os.path.join(USER_FILE_DIR, "allCode"))
if not os.path.exists(os.path.join(USER_FILE_DIR,"codeWeekTarFiles")):
    os.mkdir(os.path.join(USER_FILE_DIR,"codeWeekTarFiles"))
if not os.path.exists(os.path.join(USER_FILE_DIR,"codeZip")):
    os.mkdir(os.path.join(USER_FILE_DIR,"codeZip"))
if not os.path.exists(os.path.join(USER_FILE_DIR,"reportFile")):
    os.mkdir(os.path.join(USER_FILE_DIR,"reportFile"))
if not os.path.exists(os.path.join(USER_FILE_DIR,"upload")):
    os.mkdir(os.path.join(USER_FILE_DIR,"upload"))