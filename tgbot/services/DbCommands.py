from typing import List

from aiogram import types
from aiogram.types import Message
from sqlalchemy import select, insert, Integer
from sqlalchemy.ext.asyncio import AsyncSession

import tgbot.models as models
from bot import bot


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

    async def protect_chat(self, message: Message, session: AsyncSession) -> bool:
        is_already_protected = await self.is_chat_protected(message=message, session=session)
        if is_already_protected:
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f"Already protected. Chat_id={message.chat.id} / thread id = {message.message_thread_id}")
            return False

        sql = insert(models.ProtectedChat).values(chat_id=message.chat.id, thread_id=message.message_thread_id)
        try:
            await session.execute(sql)
            await session.commit()
            return True
        except Exception as ex:
            return False

    async def is_chat_protected(self, message: Message, session: AsyncSession) -> bool:
        sql = select(models.ProtectedChat).where(models.ProtectedChat.chat_id == message.chat.id,
                                                 models.ProtectedChat.thread_id == message.message_thread_id)
        protected_chat = (await session.execute(sql)).scalars().first()
        if protected_chat:
            return True
        return False
