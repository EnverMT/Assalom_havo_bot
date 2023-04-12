from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, BotCommandScopeChat

import bot
from tgbot.handlers.user_approval import (list_of_waiting_approval_users
                                          )
from tgbot.handlers.user_filter import (list_of_approved_users)
from tgbot.keyboards.inline import AdminMenu
from tgbot.misc.states import AdminState
from aiogram import Router
from aiogram.filters import Command
from ..filters import userFilter

router = Router()

@router.message(Command('start'), userFilter.isUserHasRole(['admin']))
async def admin_start(message: Message, state: FSMContext):
    await state.set_state(AdminState.Menu)
    await bot.bot.set_my_commands(commands=[BotCommand(command='start', description='Старт бота'),
                                                BotCommand(command='cancel', description='Отмена')],
                                      scope=BotCommandScopeChat(chat_id=message.from_user.id))

    return await bot.bot.send_message(chat_id=message.from_user.id, text="Hello, admin!!!!", reply_markup=AdminMenu)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True,
                                chat_type=types.ChatType.PRIVATE)

    dp.register_callback_query_handler(list_of_waiting_approval_users,
                                       text_contains="list_of_waiting_approval_users",
                                       state=AdminState.Menu,
                                       is_admin=True)

    # User filters
    dp.register_callback_query_handler(list_of_approved_users,
                                       state=AdminState.Menu,
                                       text="list_of_approved_users",
                                       is_admin=True)