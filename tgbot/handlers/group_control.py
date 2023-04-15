from aiogram import Router, F, enums
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot import bot
from tgbot.filters.userFilter import isUserHasRole
from tgbot.filters.userStatus import userStatus
from tgbot.services.DbCommands import DbCommands

db = DbCommands()

router = Router()
router.message.filter(F.chat.type.in_([enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]))


@router.message(F.text == "!protect", isUserHasRole(['admin']))
async def add_chat_thread_to_protection(message: Message, session: AsyncSession):
    protect_result = await db.protect_chat(message=message, session=session)
    if protect_result:
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"Protected chat_id:{message.chat.id} / thread_id:{message.message_thread_id}")


@router.message(userStatus(['notApproved']))
async def message_in_group(message: Message, session: AsyncSession):
    is_chat_protected = await db.is_chat_protected(message=message, session=session)
    if is_chat_protected:
        # until_date = datetime.now().timestamp() + 120
        # await bot.restrict_chat_member(chat_id=message.chat.id, user_id=message.from_user.id, until_date=until_date,
        #                               permissions=ChatPermissions(can_send_messages=False))
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
