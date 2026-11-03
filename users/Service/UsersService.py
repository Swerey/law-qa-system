from users.dao import UsersDao


def login(users):
    username = users.username
    password = users.password

    # 1. 检查空值
    if not (username and password):
        return {"code": 500, "msg": "账号密码不能为空", "data": None}

    # 2. 检查数据库
    result = UsersDao.find_uers_by_username(username)

    # 3. 用户不存在
    if not result:
        return {"code": 500, "msg": "账号不存在", "data": None}

    # 4. 验证密码
    if password != result[0]["password"]:
        return {"code": 500, "msg": "密码错误", "data": None}

    # 登录成功
    return {"code": 200, "msg": "登陆成功", "data": {"userId": result[0]["id"]}}


def register(users):
    username = users.username
    password = users.password

    # 1. 检查空值
    if not (username and password):
        return {"code": 500, "msg": "账号密码不能为空", "data": None}

    # 2. 用户名长度校验
    if len(username) < 3:
        return {"code": 500, "msg": "用户名至少3个字符", "data": None}

    # 3. 密码长度校验
    if len(password) < 6:
        return {"code": 500, "msg": "密码至少6个字符", "data": None}

    # 4. 检查用户是否已存在
    existing = UsersDao.find_uers_by_username(username)
    if existing:
        return {"code": 500, "msg": "该账号已被注册", "data": None}

    # 5. 注册用户
    try:
        affected = UsersDao.insert_user(username, password)
        if affected > 0:
            return {"code": 200, "msg": "注册成功", "data": None}
        else:
            return {"code": 500, "msg": "注册失败，请稍后重试", "data": None}
    except Exception as e:
        return {"code": 500, "msg": f"注册异常: {str(e)}", "data": None}
