from aiogram import Dispatcher, types
from aiogram.types import Message

from tgbot.services.DbCommands import DbCommands


db = DbCommands()


@dp.message_handlers(chat_type=types.ChatType.SUPERGROUP)
async def message_in_group(message: Message):
    protected_chats = await db.get_protected_chats(message=message)
    if message.chat.id in protected_chats:
        user = await db.select_current_user(message=message)
        if not user or not user.isApproved:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)



def register_group_control(dp: Dispatcher):
    pass
    #dp.register_message_handler(message_in_group, state='*', chat_type=types.ChatType.SUPERGROUP)