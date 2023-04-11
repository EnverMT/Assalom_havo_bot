from aiogram import Dispatcher, types
from aiogram.types import Message, BotCommand, BotCommandScopeChat

from tgbot.keyboards.inline import UserMenu
from tgbot.misc.states import UserState
from tgbot.services.DbCommands import DbCommands

db = DbCommands()


async def user_start(message: Message):
    user = await db.select_current_user(message=message)
    if not user:
        await message.bot.set_my_commands(commands=[BotCommand('start', 'Старт бота'),
                                                    BotCommand('register', 'Регистрация'),
                                                    BotCommand('cancel', 'Отмена')],
                                          scope=BotCommandScopeChat(chat_id=message.from_user.id))

        await message.bot.send_message(chat_id=message.from_user.id, text="Вы первый раз запускаете бота. Прошу пройти регистрацию. /register")
        await db.add_user(message=message)
        return

    await user.update_self_username(call=message)

    if not user.isApproved:
        await message.bot.set_my_commands(commands=[BotCommand('start', 'Старт бота'),
                                                    BotCommand('register', 'Регистрация'),
                                                    BotCommand('cancel', 'Отмена')],
                                          scope=BotCommandScopeChat(chat_id=message.from_user.id))

        await message.bot.send_message(chat_id=message.from_user.id, text="Вы еще не прошли авторизацию. Оставьте заявку (/register) и ждите ответа Домкома")
        return

    await message.bot.send_message(chat_id=message.from_user.id, text=f"Привет {user.full_name}", reply_markup=UserMenu)
    await message.bot.set_my_commands(commands=[BotCommand('start', 'Старт бота'),
                                                BotCommand('cancel', 'Отмена')],
                                      scope=BotCommandScopeChat(chat_id=message.from_user.id))
    await UserState.Menu.set()


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, state='*', commands=["start"], chat_type=types.ChatType.PRIVATE)