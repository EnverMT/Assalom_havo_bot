from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.handlers.user_approval import list_of_waiting_approval_users, waiting_approval_user, approve_user
from tgbot.handlers.user_filter import (list_of_approved_users,
                                        list_of_approved_users_by_phone,
                                        list_of_approved_users_by_phone_get_users,
                                        list_of_approved_users_by_house,
                                        list_of_approved_users_by_name,
                                        list_of_approved_users_by_name_get_users,
                                        list_of_approved_users_by_house_get_users)
from tgbot.keyboards.inline import DomkomMenu
from tgbot.misc.states import DomkomState, UserApprovalState, UserListState
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

    # User filter
    dp.register_callback_query_handler(list_of_approved_users,
                                       state=DomkomState.Menu,
                                       text="list_of_approved_users",
                                       is_domkom=True)

    dp.register_callback_query_handler(list_of_approved_users_by_phone,
                                       state=UserListState.Menu,
                                       text="list_of_approved_users_by_phone",
                                       is_domkom=True)
    dp.register_callback_query_handler(list_of_approved_users_by_house,
                                       state=UserListState.Menu,
                                       text="list_of_approved_users_by_house",
                                       is_domkom=True)

    dp.register_callback_query_handler(list_of_approved_users_by_name,
                                       state=UserListState.Menu,
                                       text="list_of_approved_users_by_name",
                                       is_domkom=True)

    dp.register_message_handler(list_of_approved_users_by_phone_get_users,
                                state=UserListState.FilterByPhone,
                                is_domkom=True)
    dp.register_message_handler(list_of_approved_users_by_name_get_users,
                                state=UserListState.FilterByName,
                                is_domkom=True)
    dp.register_message_handler(list_of_approved_users_by_house_get_users,
                                state=UserListState.FilterByHouse,
                                is_domkom=True)