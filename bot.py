import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import tgbot.handlers
from tgbot.config import load_config

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
)
logger.info("Starting bot")
config = load_config(".env")

bot = Bot(token=config.tg_bot.token, parse_mode='HTML')

storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def main():
    dp.include_router(tgbot.handlers.router)

    # start
    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")