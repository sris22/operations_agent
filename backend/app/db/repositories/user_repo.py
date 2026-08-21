from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, email: str, password_hash: str, role: UserRole = UserRole.OPERATOR
    ) -> User:
        user = User(email=email, password_hash=password_hash, role=role)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_users(self, page: int = 1, page_size: int = 20) -> Sequence[User]:
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(User).offset(offset).limit(page_size).order_by(User.created_at.desc())
        )
        return result.scalars().all()

    async def count(self) -> int:
        from sqlalchemy import func

        result = await self.db.execute(select(func.count(User.id)))
        return result.scalar_one()
