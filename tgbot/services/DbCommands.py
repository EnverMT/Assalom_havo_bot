from typing import List, Tuple

from aiogram import types
from aiogram.types.base import Boolean, Integer
from sqlalchemy import select, insert, update

from tgbot.models.models import User, Phone


class DbCommands:
    async def select_user(self, call: types.CallbackQuery, user_id: Integer) -> User:
        db_session = call.bot.get("db")
        sql = select(User).where(User.id == user_id)
        async with db_session() as session:
            result = await session.execute(sql)
            row: List[User] = result.first()
            if row:
                return row[0]
            else:
                return None

    async def select_current_user(self, message: types.Message) -> User:
        db_session = message.bot.get("db")
        sql = select(User).where(User.telegram_id == message.from_user.id)

        async with db_session() as session:
            result = await session.execute(sql)
            row: List[User] = result.first()
            if row:
                return row[0]
            else:
                return None

    async def add_user(self, message: types.Message):
        db_session = message.bot.get("db")
        sql = insert(User).values(telegram_id=message.from_user.id,
                                  full_name=message.from_user.full_name,
                                  username=message.from_user.username)
        async with db_session() as session:
            await session.execute(sql)
            return await session.commit()


    async def get_list_of_waiting_approval_users(self, call: types.CallbackQuery):
        db_session = call.bot.get("db")
        sql = select(User, Phone).join(Phone, User.id == Phone.user_id).where(User.isApproved == None)

        async with db_session() as session:
            result: (User, Phone) = await session.execute(sql)
            rows = result.all()
            if rows:
                return rows
            else:
                return None