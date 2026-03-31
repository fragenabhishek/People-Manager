"""
Bcrypt password hashing — standalone, no Flask dependency.
Drop-in replacement for flask_bcrypt methods used by AuthService.
"""
import bcrypt


class PasswordHasher:

    @staticmethod
    def generate_password_hash(password: str) -> bytes:
        """Returns bytes to match Flask-Bcrypt interface (caller calls .decode)."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    @staticmethod
    def check_password_hash(pw_hash: str, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), pw_hash.encode("utf-8"))
