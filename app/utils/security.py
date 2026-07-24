"""
密码加密、校验
"""
import bcrypt


class PasswordUtils:
    """基于 bcrypt 的密码加密与校验工具类"""

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """
        加密密码（注册时使用）
        :param plain_password: 用户输入的明文密码
        :return: 加密后的哈希字符串（包含盐值，建议数据库字段设为 VARCHAR(60)）
        """
        # 1. 将字符串转换为字节流（bcrypt 仅接受 bytes 类型）
        password_bytes = plain_password.encode('utf-8')

        # 2. 生成随机盐值并计算哈希（默认 rounds=12，兼顾安全与性能）
        hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        # 3. 将结果转回字符串，方便存入数据库
        return hashed_bytes.decode('utf-8')

    @staticmethod
    def check_password(plain_password: str, hashed_password: str) -> bool:
        """
        校验密码（登录时使用）
        :param plain_password: 用户登录时输入的明文密码
        :param hashed_password: 从数据库中取出的加密哈希值
        :return: 密码匹配返回 True，否则返回 False
        """
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        # bcrypt 会自动从 hashed_bytes 中提取盐值进行比对
        return bcrypt.checkpw(password_bytes, hashed_bytes)
