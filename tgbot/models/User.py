from typing import List

from aiogram import types
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, select, update, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from tgbot.services.Base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    full_name = Column(String(100))
    fio = Column(String(100))
    username = Column(String(50))
    isApproved = Column(Boolean)
    whoApproved = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)

    async def is_domkom(self, call: types.CallbackQuery | types.Message, user_id=0) -> bool:
        if user_id == 0:
            user_id = self.id
        db_session = call.bot.get("db")
        sql = select(User).join(Domkom, Domkom.user_id == user_id)
        async with db_session() as session:
            result = await session.execute(sql)
            row: List[User] = result.first()
            return True if row else False

    async def update_self_username(self, call: types.CallbackQuery | types.Message, session: AsyncSession):
        sql = update(User).values(username=call.from_user.username).where(User.telegram_id == self.telegram_id)
        await session.execute(sql)
        await session.commit()

    async def get_addresses(self, call: types.CallbackQuery | types.Message) -> List[Address]:
        db_session = call.bot.get("db")
        sql_addresses = select(Address) \
            .join(Propiska, Address.id == Propiska.address_id) \
            .join(User, User.id == Propiska.user_id) \
            .where(User.id == self.id)
        async with db_session() as session:
            result = await session.execute(sql_addresses)
            return result.scalars().all()

    async def get_phones(self, call: types.CallbackQuery | types.Message) -> List[Phone]:
        db_session = call.bot.get("db")
        sql = select(Phone).where(Phone.user_id == self.id)
        async with db_session() as session:
            result = await session.execute(sql)
            return result.scalars().all()

    async def get_autos(self, call: types.CallbackQuery | types.Message) -> List[Auto]:
        db_session = call.bot.get("db")
        sql = select(Auto).where(Auto.user_id == self.id)
        async with db_session() as session:
            result = await session.execute(sql)
            return result.scalars().all()