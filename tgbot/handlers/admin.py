from aiogram import Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from tgbot.keyboards.inline import AdminMenu



async def admin_start(message: Message):
    return await message.reply("Hello, admin!", reply_markup=AdminMenu)

def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)