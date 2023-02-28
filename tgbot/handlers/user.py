from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from tgbot.models.models import Address
from tgbot.services.DbCommands import DbCommands
from tgbot.keyboards.inline import UserMenu
from tgbot.misc.states import UserState

db = DbCommands()


async def user_start(message: Message):
    user = await db.select_current_user(message=message)
    if not user:
        await message.answer(text="Вы первый раз запускаете бота. Прошу пройти регистрацию")
        await db.add_user(message=message)
        return

    if not user.isApproved:
        await message.answer(text="Вы еще не прошли авторизацию. Обратитесь к администратору.")
        return

    await message.answer(text=f"Привет {user.full_name}", reply_markup=UserMenu)
    await UserState.Menu.set()


async def info_about_me(call: types.CallbackQuery):
    await call.message.edit_reply_markup()

    user = await db.select_current_user(call)
    text = f"Full name: {user.full_name}\n"

    addresses = await user.get_addresses(call=call)
    phones = await user.get_phones(call=call)
    for p in phones:
        text += f"Tel: {p[0].numbers}\n"

    await call.bot.send_message(chat_id=call.from_user.id, text=f"{text}")

    await UserState.InfoAboutMe.set()


async def cancel(message: types.Message, state: FSMContext):
    """
      Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, state='*', commands=["start"])
    dp.register_callback_query_handler(info_about_me, state=UserState.Menu)

    dp.register_message_handler(cancel, state='*', commands=['cancel'])