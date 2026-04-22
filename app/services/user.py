from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, username: str, email: str, password: str):
        return await self.repo.get_or_create(username=username, email=email, password=password)

    async def login(self, username: str, password: str) -> User | None:
        return await self.repo.authenticate(username=username, password=password)

    async def get_all(self) -> list[User]:
        return await self.repo.get_all()

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.repo.get_by_id(user_id=user_id)
