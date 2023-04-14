import aiogram
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, BotCommandScopeChat
from sqlalchemy.ext.asyncio import AsyncSession

from bot import bot
from tgbot.keyboards.inline import UserMenu
from tgbot.misc.states import UserState
from tgbot.services.DbCommands import DbCommands

db = DbCommands()

router = Router()
router.message.filter(F.chat.type == aiogram.enums.ChatType.PRIVATE)


@router.message(Command('start'))
async def user_start(message: Message, state: FSMContext, session: AsyncSession):
    user = await db.select_current_user(message=message, session=session)
    if not user:
        await bot.set_my_commands(commands=[BotCommand(command='start', description='Старт бота'),
                                            BotCommand(command='register', description='Регистрация'),
                                            BotCommand(command='cancel', description='Отмена')],
                                  scope=BotCommandScopeChat(chat_id=message.from_user.id))

        await bot.send_message(chat_id=message.from_user.id,
                               text="Вы первый раз запускаете бота. Прошу пройти регистрацию. /register")
        await db.add_user(message=message, session=session)
        return

    await user.update_self_username(call=message, session=session)

    if not user.isApproved:
        await bot.set_my_commands(commands=[BotCommand(command='start', description='Старт бота'),
                                            BotCommand(command='register', description='Регистрация'),
                                            BotCommand(command='cancel', description='Отмена')],
                                  scope=BotCommandScopeChat(chat_id=message.from_user.id))

        await bot.send_message(chat_id=message.from_user.id,
                               text="Вы еще не прошли авторизацию. Оставьте заявку (/register) и ждите ответа Домкома")
        return

    await bot.send_message(chat_id=message.from_user.id, text=f"Привет {user.full_name}", reply_markup=UserMenu)
    await bot.set_my_commands(commands=[BotCommand(command='start', description='Старт бота'),
                                        BotCommand(command='cancel', description='Отмена')],
                              scope=BotCommandScopeChat(chat_id=message.from_user.id))
    await state.set_state(UserState.Menu)