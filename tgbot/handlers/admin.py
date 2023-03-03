from aiogram import Dispatcher
from aiogram.types import Message, BotCommand, BotCommandScopeChat

from tgbot.handlers.domkom import (list_of_approved_users,
                                   list_of_approved_users_by_phone,
                                   list_of_approved_users_by_house,
                                   list_of_approved_users_by_name,
                                   list_of_approved_users_by_phone_get_users, list_of_approved_users_by_name_get_users,
                                   list_of_approved_users_by_house_get_users)

from tgbot.handlers.user_approval import (list_of_waiting_approval_users,
                                   waiting_approval_user,
                                   approve_user
                                   )
from tgbot.handlers.domkom_approval import (list_of_domkoms,
                                            add_new_domkom,
                                            assign_new_domkom)
from tgbot.keyboards.inline import AdminMenu
from tgbot.misc.states import AdminState, UserApprovalState, DomkomControlState, UserListState


async def admin_start(message: Message):
    await AdminState.Menu.set()
    await message.bot.set_my_commands(commands=[BotCommand('start', 'Старт бота'),
                                                BotCommand('cancel', 'Отмена')],
                                      scope=BotCommandScopeChat(chat_id=message.from_user.id))

    return await message.reply("Hello, admin!!!!", reply_markup=AdminMenu)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)

    dp.register_callback_query_handler(list_of_waiting_approval_users,
                                       text_contains="list_of_waiting_approval_users",
                                       state=AdminState.Menu,
                                       is_admin=True)
    dp.register_callback_query_handler(waiting_approval_user,
                                       state=UserApprovalState.ListOfWaitingApprovalUsers,
                                       is_admin=True)
    dp.register_callback_query_handler(approve_user,
                                       state=UserApprovalState.WaitingApprovalUser,
                                       is_admin=True)


    dp.register_callback_query_handler(list_of_domkoms,
                                       state=AdminState.Menu,
                                       text_contains="list_of_domkoms",
                                       is_admin=True)

    dp.register_callback_query_handler(add_new_domkom,
                                       state=AdminState.Menu,
                                       text_contains="add_new_domkom",
                                       is_admin=True)

    dp.register_callback_query_handler(assign_new_domkom,
                                       state=DomkomControlState.AddNewDomkom,
                                       is_admin=True)

    dp.register_callback_query_handler(list_of_approved_users,
                                       state=AdminState.Menu,
                                       text="list_of_approved_users",
                                       is_admin=True)

    dp.register_callback_query_handler(list_of_approved_users_by_phone,
                                       state=UserListState.Menu,
                                       text="list_of_approved_users_by_phone",
                                       is_admin=True)

    dp.register_message_handler(list_of_approved_users_by_phone_get_users,
                                state=UserListState.FilterByPhone,
                                is_admin=True)

    dp.register_callback_query_handler(list_of_approved_users_by_house,
                                       state=UserListState.Menu,
                                       text="list_of_approved_users_by_house",
                                       is_admin=True)

    dp.register_callback_query_handler(list_of_approved_users_by_name,
                                       state=UserListState.Menu,
                                       text="list_of_approved_users_by_name",
                                       is_admin=True)
    dp.register_message_handler(list_of_approved_users_by_name_get_users,
                                state=UserListState.FilterByName,
                                is_admin=True)
    dp.register_message_handler(list_of_approved_users_by_house_get_users,
                                state=UserListState.FilterByHouse,
                                is_admin=True)