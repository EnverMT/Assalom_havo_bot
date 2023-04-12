from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tgbot.config import load_config
from tgbot.services.Base import Base

config = load_config(".env")

engine = create_async_engine(
    f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.database}",
    future=True
)


async def get_db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )