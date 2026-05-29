import bcrypt


def hash_password(password: str) -> str:
    """使用 bcrypt 哈希密码。"""

    if not password:
        raise ValueError("密码不能为空")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, stored_password: str) -> bool:
    """校验密码。

    兼容早期演示数据中的明文 demo，后续新用户统一使用 bcrypt。
    """

    if not plain_password or not stored_password:
        return False
    if stored_password.startswith("$2a$") or stored_password.startswith("$2b$") or stored_password.startswith("$2y$"):
        return bcrypt.checkpw(plain_password.encode("utf-8"), stored_password.encode("utf-8"))
    return plain_password == stored_password

