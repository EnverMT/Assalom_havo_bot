from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.handlers.common import list_of_waiting_approval_users, waiting_approval_user, approve_user
from tgbot.keyboards.inline import DomkomMenu
from tgbot.misc.states import DomkomState, UserApprovalState
from tgbot.services.DbCommands import DbCommands

db = DbCommands()


async def domkom_start(message: Message, state: FSMContext):
    await DomkomState.Menu.set()
    return await message.reply("Hello, domkom!", reply_markup=DomkomMenu)


def register_domkom(dp: Dispatcher):
    dp.register_message_handler(domkom_start, commands=["start"], state="*", is_domkom=True)
    dp.register_callback_query_handler(list_of_waiting_approval_users,
                                       text_contains="list_of_waiting_approval_users",
                                       state=DomkomState.Menu,
                                       is_domkom=True)
    dp.register_callback_query_handler(waiting_approval_user,
                                       state=UserApprovalState.ListOfWaitingApprovalUsers,
                                       is_domkom=True)
    dp.register_callback_query_handler(approve_user,
                                       state=UserApprovalState.WaitingApprovalUser,
                                       is_domkom=True)