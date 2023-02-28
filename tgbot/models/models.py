from typing import List, Tuple

from aiogram import types
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, TIMESTAMP, DateTime, select
from sqlalchemy import sql
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.sql import func

from tgbot.services.Base import Base

class Phone(Base):
    __tablename__ = 'phones'

    id = Column(Integer, primary_key=True)
    numbers = Column(String(15), unique=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return "<Phone(id='{}', numbers='{}', user_id='{}')>".format(
            self.id, self.numbers, self.user_id)


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    house = Column(Integer, nullable=False)
    apartment = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return "<Address(id='{}', house='{}', apartment='{}', user_id='{}')>".format(
            self.id, self.house, self.apartment, self.user_id)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    full_name = Column(String(100))
    username = Column(String(50))
    isApproved = Column(Boolean)
    whoApproved = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)

    async def get_addresses(self, call: types.CallbackQuery) -> List[Tuple[Address]]:
        db_session = call.bot.get("db")
        sql = select(User).where(User.telegram_id == call.from_user.id)
        async with db_session() as session:
            result = await session.execute(sql)
            row: List[User] = result.first()
            if row:
                user = row[0]
            else:
                return
        sql = select(Address).where(Address.user_id == user.id)
        async with db_session() as session:
            result = await session.execute(sql)
            return result.all()

    async def get_phones(self, call: types.CallbackQuery | types.Message) -> List[Tuple[Phone]]:
        db_session = call.bot.get("db")
        sql = select(User).where(User.telegram_id == call.from_user.id)
        async with db_session() as session:
            result = await session.execute(sql)
            row: List[User] = result.first()
            if row:
                user = row[0]
            else:
                return
        sql = select(Phone).where(Phone.user_id == user.id)
        async with db_session() as session:
            result = await session.execute(sql)
            return result.all()