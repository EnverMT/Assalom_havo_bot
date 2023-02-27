from typing import List
from aiogram import types
from sqlalchemy import select, insert
from tgbot.models.models import User, Phone


class DbCommands:
    async def select_user(self, message: types.Message):
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
        user : User = await self.select_user(message=message)
        db_session = message.bot.get("db")
        sql = insert(Phone).values(user_id=user.id,
                                   numbers=str(message.contact.phone_number))
        async with db_session() as session:
            await session.execute(sql)
            return await session.commit()