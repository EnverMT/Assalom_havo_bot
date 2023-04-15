from typing import List

from aiogram import types
from sqlalchemy import select, insert, Integer
from sqlalchemy.ext.asyncio import AsyncSession

import tgbot.models as models


class DbCommands:
    async def select_user(self, user_id: int, session: AsyncSession) -> models.User | None:
        sql = select(models.User).where(models.User.id == user_id)
        result = await session.execute(sql)
        row = result.first()
        if row:
            return row[0]
        else:
            return None

    async def select_current_user(self, message: types.Message | types.CallbackQuery,
                                  session: AsyncSession) -> models.User | None:
        sql = select(models.User).where(models.User.telegram_id == message.from_user.id)
        result = await session.execute(sql)
        row = result.first()
        if row:
            return row[0]
        else:
            return None

    async def add_user(self, message: types.Message, session: AsyncSession):
        sql = insert(models.User).values(telegram_id=message.from_user.id,
                                         full_name=message.from_user.full_name,
                                         username=message.from_user.username)
        await session.execute(sql)
        return await session.commit()

    async def get_list_of_waiting_approval_users(self, session: AsyncSession):
        sql = select(models.User, models.Phone).join(models.Phone, models.User.id == models.Phone.user_id).where(
            models.User.isApproved == None)
        result: (models.User, models.Phone) = await session.execute(sql)
        rows = result.all()
        if rows:
            return rows
        else:
            return None

    async def get_protected_chats(self, session: AsyncSession) -> List[Integer]:
        sql = select(models.ProtectedChat)
        result = await session.execute(sql)
        chatList = []
        for chat in result.scalars().all():
            chatList.append(chat.chat_id)
        return chatList