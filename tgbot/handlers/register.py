from typing import List

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy import select
from tgbot.models.models import User
from tgbot.keyboards.reply import contact_request

"""
[ ] To do validation of all inputs in all methods
[ ] To use memoryStorage, and save data to Database at final step only
"""


async def check_register_status(message: types.Message, state : FSMContext):
    db_session = message.bot.get("db")
    sql = select(User).where(User.user_id == message.from_user.id)

    async with db_session() as session:
        result = await session.execute(sql)
        row: List[User] = result.first()
        if row:
            await message.answer(text=f"Вы готовы пройти Регистрацию {row[0].full_name} ?", reply_markup=contact_request)


def register_register_menu(dp: Dispatcher):
    dp.register_message_handler(check_register_status, commands=["register"], state='*')