from aiogram import Dispatcher, types, Router, F, enums
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

from tgbot.filters.userFilter import isUserHasRole
from tgbot.handlers.user_approval import list_of_waiting_approval_users
from tgbot.handlers.user_filter import (list_of_approved_users)
from tgbot.keyboards.inline import DomkomMenu
from tgbot.misc.states import DomkomState

router = Router()
router.message.filter(F.chat.type == enums.ChatType.PRIVATE)
router.message.filter(isUserHasRole(['domkom']))


@router.message(Command('start'))
async def domkom_start(message: Message, state: FSMContext):
    await state.set_state(DomkomState.Menu)
    return await message.reply("Hello, domkom!", reply_markup=DomkomMenu)


def register_domkom(dp: Dispatcher):


    # User filter
    dp.register_callback_query_handler(list_of_approved_users,
                                       state=DomkomState.Menu,
                                       text="list_of_approved_users",
                                       is_domkom=True)

    pass
