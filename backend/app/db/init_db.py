import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base_class import Base
from app.db.session import engine
from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import get_settings

settings = get_settings()


async def init_db() -> None:
    """
    Инициализация базы данных.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        if not users:
            test_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True,
            )
            session.add(test_user)
            await session.commit()


async def main() -> None:
    await init_db()


if __name__ == "__main__":
    asyncio.run(main())
