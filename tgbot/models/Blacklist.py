from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, select, update, Integer

from tgbot.services.Base import Base


class Blacklist(Base):
    __tablename__ = 'blacklist'

    id = Column(Integer, primary_key=True)
    text = Column(String)

    def __init__(self, text: str):
        self.text = text

    @classmethod
    async def isTextBlacklisted(cls, text: str, session: AsyncSession) -> bool:
        sql = select(Blacklist).where(Blacklist.text == text)
        result = await session.execute(sql)
        return len(result.scalars().all()) >= 1
