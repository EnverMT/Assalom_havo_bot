from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.handlers.user_approval import list_of_waiting_approval_users
from tgbot.handlers.user_filter import (list_of_approved_users)
from tgbot.keyboards.inline import DomkomMenu
from tgbot.misc.states import DomkomState
from tgbot.services.DbCommands import DbCommands

db = DbCommands()


async def domkom_start(message: Message, state: FSMContext):
    await DomkomState.Menu.set()
    return await message.reply("Hello, domkom!", reply_markup=DomkomMenu)


def register_domkom(dp: Dispatcher):
    dp.register_message_handler(domkom_start, commands=["start"], state="*", is_domkom=True,
                                chat_type=types.ChatType.PRIVATE)
    dp.register_callback_query_handler(list_of_waiting_approval_users,
                                       text_contains="list_of_waiting_approval_users",
                                       state=DomkomState.Menu,
                                       is_domkom=True)

    # User filter
    dp.register_callback_query_handler(list_of_approved_users,
                                       state=DomkomState.Menu,
                                       text="list_of_approved_users",
                                       is_domkom=True)