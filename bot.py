import asyncio
import logging

from aiogram import Bot, Dispatcher

from aiogram.types import BotCommand


from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.user import register_user
from tgbot.handlers.register import register_register_menu
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.services.database import create_db




def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)
    register_register_menu(dp)
async def on_startup(config):
    await create_db(config)


async def set_default_commands(bot : Bot):
    return await bot.set_my_commands(commands=[BotCommand('start', 'Старт бота'),
                                               BotCommand('register', 'Пройти регистрацию'),
                                               BotCommand('cancel', 'Отмена')])


async def main():
    from load_all import bot, config, dp
    bot['config'] = config

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    await on_startup(config)
    await set_default_commands(bot)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
