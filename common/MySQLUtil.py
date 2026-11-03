import pymysql
import os

def mysql_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        port=3306,
        password=os.getenv("BASE_PASSWORD"),
        database="feifan_ai",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

def mysql_close(cur,conn):
    cur.close()
    conn.close()
