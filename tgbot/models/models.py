from typing import List, Tuple

from aiogram import types
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, select, UniqueConstraint, update
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.sql import func

from tgbot.services.Base import Base


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    house = Column(Integer, nullable=False)
    apartment = Column(Integer, nullable=False)
    gaz_litsevoy_schet = Column(Integer)
    owner_fio = Column(String(100))
    owner_tel = Column(String(20))
    room_size = Column(String(20))
    kadastr_number = Column(String(30))
    gaz_schetchik_nomer = Column(String(20))
    musor_ls = Column(String(30))

    def __repr__(self):
        return "<Address(id='{}', house='{}', apartment='{}')>".format(
            self.id, self.house, self.apartment)


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


class Domkom(Base):
    __tablename__ = 'domkoms'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    telegram_id = Column(BigInteger, nullable=False)
    whoAssigned = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return "<Domkom(id='{}', user_id='{}', whoAssigned='{}')>".format(
            self.id, self.user_id, self.whoAssigned)


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

    async def is_domkom(self, call: types.CallbackQuery | types.Message, user_id = 0) -> bool:
        if user_id == 0:
            user_id = self.id
        db_session = call.bot.get("db")
        sql = select(User).join(Domkom, Domkom.user_id == user_id)
        async with db_session() as session:
            result = await session.execute(sql)
            row: List[User] = result.first()
            return True if row else False

    async def update_self_username(self, call: types.CallbackQuery | types.Message):
        db_session = call.bot.get("db")
        print(call.from_user.username)
        sql = update(User).values(username=call.from_user.username).where(User.telegram_id == self.telegram_id)
        async with db_session() as session:
            await session.execute(sql)
            await session.commit()


    async def get_addresses(self, call: types.CallbackQuery | types.Message) -> List[Tuple[Address]]:
        db_session = call.bot.get("db")
        sql_addresses = select(Address) \
            .join(Propiska, Address.id == Propiska.address_id) \
            .join(User, User.id == Propiska.user_id) \
            .where(User.id == self.id)
        async with db_session() as session:
            result =  await session.execute(sql_addresses)
            return result.all()


    async def get_phones(self, call: types.CallbackQuery | types.Message) -> List[Tuple[Phone]]:
        db_session = call.bot.get("db")
        sql = select(Phone).where(Phone.user_id == self.id)
        async with db_session() as session:
            result = await session.execute(sql)
            return result.all()


class Propiska(Base):
    __tablename__ = 'propiska'
    __table_args__ = (UniqueConstraint('user_id', 'address_id'),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    address_id = Column(Integer, ForeignKey("address.id", onupdate="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return "<Propiska(id='{}', user_id='{}', address_id='{}')>".format(
            self.id, self.user_id, self.address_id)