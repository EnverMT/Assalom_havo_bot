from typing import List, Tuple

from aiogram import types
from sqlalchemy import select, insert, update, Integer

from tgbot.models.models import User, Phone, ProtectedChat
from sqlalchemy.ext.asyncio import AsyncSession


class DbCommands:
    async def select_user(self, call: types.CallbackQuery, user_id: Integer, session: AsyncSession) -> User | None:
        sql = select(User).where(User.id == user_id)
        result = await session.execute(sql)
        row: List[User] = result.first()
        if row:
            return row[0]
        else:
            return None

    async def select_current_user(self, message: types.Message | types.CallbackQuery, session: AsyncSession) -> User | None:
        sql = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.execute(sql)
        row: List[User] = result.first()
        if row:
            return row[0]
        else:
            return None

    async def add_user(self, message: types.Message, session: AsyncSession):
        sql = insert(User).values(telegram_id=message.from_user.id,
                                  full_name=message.from_user.full_name,
                                  username=message.from_user.username)
        async with db_session() as session:
            await session.execute(sql)
            return await session.commit()


    async def get_list_of_waiting_approval_users(self, call: types.CallbackQuery, session: AsyncSession):
        sql = select(User, Phone).join(Phone, User.id == Phone.user_id).where(User.isApproved == None)

        async with db_session() as session:
            result: (User, Phone) = await session.execute(sql)
            rows = result.all()
            if rows:
                return rows
            else:
                return None

    async def get_protected_chats(self, message: types.Message, session: AsyncSession) -> List[Integer]:
        sql = select(ProtectedChat)

        async with db_session() as session:
            result = await session.execute(sql)
            chatList = []
            for chat in result.scalars().all():
                chatList.append(chat.chat_id)
            return chatList