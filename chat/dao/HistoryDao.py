from common import MySQLUtil

def find_history_by_user_id(user_id):
    conn = MySQLUtil.mysql_conn()
    cur = conn.cursor()
    sql = """
        SELECT h.* FROM history h
        LEFT JOIN users u ON h.history_fk_users =u.id
        WHERE u.id = %s AND parent_id = 0
        ORDER BY h.create_time DESC
    """
    cur.execute(sql,[user_id])
    result = cur.fetchall()
    MySQLUtil.mysql_close(cur,conn)
    return result
def find_messages_by_history_id(history_id):
    conn = MySQLUtil.mysql_conn()
    cur = conn.cursor()
    sql = """
        SELECT * FROM history 
        WHERE history_id = %s OR parent_id = %s
        ORDER BY create_time ASC
    """
    cur.execute(sql,[history_id,history_id])
    result = cur.fetchall()
    MySQLUtil.mysql_close(cur,conn)
    return result
def insert_history(question,answer,parent_id,user_id):
    conn = MySQLUtil.mysql_conn()
    cur = conn.cursor()
    sql = """
        INSERT INTO history 
            (question,answer,create_time,parent_id,history_fk_users) 
        VALUES 
            (%s, %s, NOW(), %s, %s)
    """
    cur.execute(sql,[question,answer,parent_id,user_id])
    conn.commit()
    new_id = cur.lastrowid
    MySQLUtil.mysql_close(cur,conn)
    return new_id
def search_history_by_keyword(user_id,keyword):
    conn = MySQLUtil.mysql_conn()
    cur = conn.cursor()
    sql = """
        SELECT h.* FROM history h
        LEFT JOIN users u ON h.history_fk_users =u.id
        WHERE u.id = %s AND (h.question LIKE %s OR h.answer LIKE %s)
        ORDER BY h.create_time DESC
    """
    like_keyword = f"%{keyword}%"
    cur.execute(sql,[user_id, like_keyword, like_keyword])
    result = cur.fetchall()
    MySQLUtil.mysql_close(cur,conn)
    return result
def delete_history_root_id(root_id):
    conn = MySQLUtil.mysql_conn()
    cur = conn.cursor()
    sql = """
        DELETE FROM history 
        WHERE history_id = %s OR parent_id = %s
    """
    cur.execute(sql,[root_id,root_id])
    conn.commit()
    MySQLUtil.mysql_close(cur,conn)