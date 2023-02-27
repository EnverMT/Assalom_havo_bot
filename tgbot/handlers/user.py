from typing import List

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from tgbot.models.models import User
from tgbot.services.DbCommands import DbCommands

db = DbCommands()


async def user_start(message: Message):
    user = await db.select_user(message=message)
    if not user:
        await message.answer(text="Вы первый раз запускаете бота. Прошу пройти регистрацию")
        await add_user(message)
        return

    await message.answer(text=f"Привет {user.full_name}")

async def add_user(message: Message):
    await db.add_user(message=message)


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
    dp.register_message_handler(user_start, commands=["start"], state=None)
    dp.register_message_handler(cancel, state='*', commands=['cancel'])