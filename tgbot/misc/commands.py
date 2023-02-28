from aiogram.types import BotCommand, BotCommandScopeChat
from aiogram import Bot

async def set_menu_for_unregistered_users(bot : Bot):
    return await bot.set_my_commands(commands=[BotCommand('start', 'Старт бота'),
                                               BotCommand('register', 'Пройти регистрацию'),
                                               BotCommand('cancel', 'Отмена')])