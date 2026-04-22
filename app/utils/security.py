import bcrypt


class PasswordService:

    @classmethod
    def hash(cls, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password=password.encode("utf-8"), salt=salt).decode("utf-8")

    @classmethod
    def verify(cls, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(password=plain.encode("utf-8"), hashed_password=hashed.encode("utf-8"))
