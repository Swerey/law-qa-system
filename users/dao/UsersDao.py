from common import MySQLUtil


def find_uers_by_username(username):
    conn = MySQLUtil.mysql_conn()
    cur = conn.cursor()
    sql = "SELECT * FROM users WHERE username = %s"
    cur.execute(sql, [username])
    result = cur.fetchall()
    MySQLUtil.mysql_close(cur, conn)
    return result


def insert_user(username, password):
    conn = MySQLUtil.mysql_conn()
    cur = conn.cursor()
    sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
    cur.execute(sql, [username, password])
    conn.commit()
    affected = cur.rowcount
    MySQLUtil.mysql_close(cur, conn)
    return affected


if __name__ == '__main__':
    print(find_uers_by_username("cc"))

