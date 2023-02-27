from aiogram import Dispatcher, types
from aiogram.types import Message
from tgbot.keyboards.inline import AdminMenu
from tgbot.services.DbCommands import DbCommands
from tgbot.misc.states import AdminState
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


db = DbCommands()

async def admin_start(message: Message):
    await AdminState.Menu.set()
    return await message.reply("Hello, admin!", reply_markup=AdminMenu)


async def list_of_waiting_approval_users(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    users = await db.get_list_of_waiting_approval_users(call=call)
    inline_user_keyboard = InlineKeyboardMarkup(row_width=1)
    for user, phone in users:
        text = f"Имя: {user.full_name}\n"
        text += f"Phone: {phone.numbers}"
        inline_user_keyboard.add(InlineKeyboardButton(text=text, callback_data=user.id))
    await call.bot.send_message(chat_id=call.from_user.id, text="List of waiting approval users", reply_markup=inline_user_keyboard)
    await AdminState.ListOfWaitingApprovalUsers.set()

def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_callback_query_handler(list_of_waiting_approval_users,
                                       text_contains="list_of_waiting_approval_users",
                                       state=AdminState.Menu,
                                       is_admin=True)