from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from tgbot.keyboards.inline import UserMenu

from tgbot.services.database import DBCommands

database = DBCommands()

async def user_start(message: Message):
    user = await database.get_user(message.from_user.id)
    if not user:
        await message.answer("Вы еще не прошли регистрацию")
        return

    if user.isRegistered:
        await message.reply("Добро пожаловать в бот Ассалом Хаво!", reply_markup=UserMenu)
        return

    if user.awaiting_register:
        await message.answer("Ваша заявка под рассмотрением")
        return

async def cancel(message: types.Message, state : FSMContext):
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
