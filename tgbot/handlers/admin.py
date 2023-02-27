from typing import List, Tuple

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
from sqlalchemy import select

from tgbot.keyboards.inline import AdminMenu
from tgbot.misc.states import AdminState
from tgbot.models.models import User, Phone
from tgbot.services.DbCommands import DbCommands

db = DbCommands()


async def admin_start(message: Message):
    await AdminState.Menu.set()
    return await message.reply("Hello, admin!", reply_markup=AdminMenu)


async def list_of_waiting_approval_users(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    users = await db.get_list_of_waiting_approval_users(call=call)
    inline_user_keyboard = InlineKeyboardMarkup(row_width=1)
    if not users:
        await call.bot.send_message(chat_id=call.from_user.id, text="No users waiting")
        return

    for user, phone in users:
        text = f"Имя: {user.full_name}\t"
        text += f"Phone: {phone.numbers}"
        inline_user_keyboard.add(InlineKeyboardButton(text=text, callback_data=user.id))
    await call.bot.send_message(chat_id=call.from_user.id, text="List of waiting approval users",
                                reply_markup=inline_user_keyboard)
    await AdminState.ListOfWaitingApprovalUsers.set()


async def waiting_approval_user(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    user: User = await db.select_user(call=call, user_id=int(call.data))
    text = f"Name: {user.full_name}\n"

    db_session = call.bot.get("db")
    sql = select(Phone).where(Phone.user_id == int(user.id))
    async with db_session() as session:
        result = await session.execute(sql)
        rows: List[Tuple[Phone]] = result.all()
        if rows:
            for r in rows:
                text += f"Tel: {r[0].numbers}"

    keyb = InlineKeyboardMarkup(row_width=1)
    keyb.add(InlineKeyboardButton(text="Принять", callback_data="Approve"))
    keyb.add(InlineKeyboardButton(text="Отказать", callback_data="Deny"))

    await call.bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyb)
    await state.update_data(under_approval_user=user.id)
    await AdminState.WaitingApproval.set()


async def approve_user(call: types.CallbackQuery, state: FSMContext):
    pass


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_callback_query_handler(list_of_waiting_approval_users,
                                       text_contains="list_of_waiting_approval_users",
                                       state=AdminState.Menu,
                                       is_admin=True)
    dp.register_callback_query_handler(waiting_approval_user,
                                       state=AdminState.ListOfWaitingApprovalUsers,
                                       is_admin=True)
    dp.register_callback_query_handler(approve_user, state=AdminState.WaitingApproval, is_admin=True)
