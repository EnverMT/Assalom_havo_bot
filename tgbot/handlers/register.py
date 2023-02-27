from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy import select
from tgbot.models.models import User

"""
[ ] To do validation of all inputs in all methods
[ ] To use memoryStorage, and save data to Database at final step only
"""

async def check_register_status(message: types.Message, state : FSMContext):
    db_session = message.bot.get("db")
    sql = select(User).limit(1)

    async with db_session() as session:
        user = await session.execute(sql)
        await message.answer(text=f"User: {user.user_id}", parse_mode="HTML")

    if not user:
        await message.answer(f"User not found")
        return

def register_register_menu(dp: Dispatcher):
    dp.register_message_handler(check_register_status, commands=["register"], state='*')