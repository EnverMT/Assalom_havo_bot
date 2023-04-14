from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton

# contact_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
#     KeyboardButton(text='Отправить свой контакт ☎️', request_contact=True)
# )

contact_request = types.ReplyKeyboardMarkup(resize_keyboard=True)
contact_request.add(types.KeyboardButton(text="Отправить номер телефона 📱", request_contact=True))