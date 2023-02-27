from typing import List
from aiogram import types
from aiogram.types.base import Boolean, Integer
from sqlalchemy import select, insert
from sqlalchemy.orm import query

from tgbot.models.models import User, Phone


class DbCommands:
    async def select_user(self, call:types.CallbackQuery, user_id : Integer) -> User | None:
        db_session = call.bot.get("db")
        sql = select(User).where(User.id == user_id)
        async with db_session() as session:
            result = await session.execute(sql)
            row: List[User] = result.first()
            if row:
                return row[0]
            else:
                return None

    async def select_current_user(self, message: types.Message) -> User | None:
        db_session = message.bot.get("db")
        sql = select(User).where(User.user_id == message.from_user.id)

        async with db_session() as session:
            result = await session.execute(sql)
            row: List[User] = result.first()
            if row:
                return row[0]
            else:
                return None

    async def add_user(self, message: types.Message):
        db_session = message.bot.get("db")
        sql = insert(User).values(user_id=message.from_user.id,
                                  full_name=message.from_user.full_name)
        async with db_session() as session:
            await session.execute(sql)
            return await session.commit()

    async def add_phone(self, message: types.Message):
        user: User = await self.select_current_user(message=message)
        db_session = message.bot.get("db")
        sql = insert(Phone).values(user_id=user.id,
                                   numbers=str(message.contact.phone_number))
        async with db_session() as session:
            await session.execute(sql)
            return await session.commit()

    async def get_user_phones(self, message: types.Message) -> List[Phone]:
        user = await self.select_current_user(message=message)
        db_session = message.bot.get("db")
        sql = select(Phone).where(Phone.user_id == user.id)
        async with db_session() as session:
            result = await session.execute(sql)
            rows = result.all()

            if rows:
                _list = list()
                for r in rows:
                    _list.append(r[0])
                return _list


    async def is_phone_exist(self, message: types.Message) -> Boolean:
        db_session = message.bot.get("db")
        user = await self.select_current_user(message)
        sql = select(Phone).where(Phone.user_id == user.id)
        async with db_session() as session:
            result = await session.execute(sql)
            rows = result.all()
            if rows:
                return True
            else:
                return False


    async def get_list_of_waiting_approval_users(self, call:types.CallbackQuery):
        db_session = call.bot.get("db")
        sql = select(User, Phone).join(Phone, User.id == Phone.user_id).where(User.isApproved == None)

        async with db_session() as session:
            result : (User, Phone) = await session.execute(sql)
            rows= result.all()
            if rows:
                return rows
            else:
                return None