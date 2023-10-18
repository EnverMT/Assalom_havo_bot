from aiogram import Router, F, enums
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, BotCommandScopeChat

from bot import bot
from tgbot.filters.userFilter import isUserHasRole
from tgbot.keyboards.inline import AdminMenu
from tgbot.misc.states import AdminState

router = Router()
router.message.filter(F.chat.type == enums.ChatType.PRIVATE)
router.message.filter(isUserHasRole(['admin']))


@router.message(Command('start'))
async def admin_start(message: Message, state: FSMContext):
    await state.set_state(AdminState.Menu)
    await bot.set_my_commands(commands=[BotCommand(command='start', description='Старт бота'),
                                        BotCommand(command='cancel', description='Отмена')],
                              scope=BotCommandScopeChat(chat_id=message.from_user.id))

    return await bot.send_message(chat_id=message.from_user.id, text="Hello, admin v4", reply_markup=AdminMenu)
