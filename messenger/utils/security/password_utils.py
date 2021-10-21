import hashlib
from datetime import datetime


class PasswordUtils:
    @staticmethod
    def get_password_hash(password: str, created_at: datetime) -> str:
        salt = hashlib.sha256(str(created_at.timestamp()).encode()).hexdigest()
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash
