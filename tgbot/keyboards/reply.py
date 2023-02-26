from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

contact_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Отправить свой контакт ☎️', request_contact=True)
)