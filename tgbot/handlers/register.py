from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from tgbot.models.models import User
from tgbot.keyboards.reply import contact_request
from tgbot.misc.states import RegisterState
from tgbot.services.DbCommands import DbCommands

"""
[ ] To do validation of all inputs in all methods
[ ] To use memoryStorage, and save data to Database at final step only
"""

db = DbCommands()

async def check_register_status(message: types.Message, state : FSMContext):
    user = await db.select_user(message=message)
    if not user:
        return
    await message.answer(text=f"Вы готовы пройти Регистрацию {user.full_name} ?", reply_markup=contact_request)


async def register_get_contact_callback(message: types.Message) -> User:
   pass


def register_register_menu(dp: Dispatcher):
    dp.register_message_handler(check_register_status, commands=["register"], state='*')
    dp.register_message_handler(register_get_contact_callback,
                                state=RegisterState.ReadyToRegister,
                                content_types=types.ContentType.CONTACT)