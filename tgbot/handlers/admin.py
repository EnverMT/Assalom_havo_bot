from typing import List
from aiogram import Dispatcher, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from tgbot.models.models import User
from tgbot.keyboards.inline import AdminMenu
from load_all import dp
from tgbot.misc.states import AdminRegisterState


async def admin_start(message: Message):
    return await message.reply("Hello, admin!", reply_markup=AdminMenu)


async def get_awaiting_register_users(message: Message):
    await AdminRegisterState.AwaitingUsersList.set()

    users : List[User] = await User.query.where(User.awaiting_register == True).gino.all()
    markup = InlineKeyboardMarkup(row_width=1)

    for user in users:
        markup.add(InlineKeyboardButton(text=user.fio, callback_data=user.user_id))

    await dp.bot.send_message(chat_id=message.from_user.id, text="Список", reply_markup=markup)


async def register_user(call : CallbackQuery):
    await AdminRegisterState.ApprovalUsers.set()
    user = await User.query.where(User.user_id == int(call.data)).gino.first()
    await user.update(isRegistered = True).apply()
    await user.update(awaiting_register=False).apply()
    await call.message.answer(text=f"User: {user.fio} has been registered")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_callback_query_handler(get_awaiting_register_users, text_contains="list_of_awayting_users", is_admin=True)
    dp.register_callback_query_handler(register_user, state=AdminRegisterState.AwaitingUsersList, is_admin=True)


