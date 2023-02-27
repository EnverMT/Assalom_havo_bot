from typing import List

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from sqlalchemy import insert, select

from tgbot.models.models import User


async def user_start(message: Message):
    await message.answer("Hello user")
    db_session = message.bot.get("db")
    sql = select(User).where(User.user_id == message.from_user.id)

    async with db_session() as session:
        result = await session.execute(sql)
        row: List[User] = result.first()
        if row:
            await message.answer(text=f"Привет {row[0].full_name}")
        else:
            await add_user(message)


async def add_user(message: Message):
    db_session = message.bot.get("db")
    sql = insert(User).values(user_id=message.from_user.id,
                              full_name=message.from_user.full_name)
    async with db_session() as session:
        await session.execute(sql)
        await session.commit()
    #await message.answer(text=f"User added", parse_mode='HTML')


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