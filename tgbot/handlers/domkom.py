from aiogram import Router, F, enums
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.filters.userFilter import isUserHasRole
from tgbot.keyboards.inline import DomkomMenu
from tgbot.misc.states import DomkomState

router = Router()
router.message.filter(F.chat.type == enums.ChatType.PRIVATE)
router.message.filter()


@router.message(Command('start'), isUserHasRole(['domkom']))
async def domkom_start(message: Message, state: FSMContext):
    await state.set_state(DomkomState.Menu)
    return await message.reply("Hello, domkom!", reply_markup=DomkomMenu)
