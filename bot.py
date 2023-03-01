import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter, DomkomFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.domkom import register_domkom
from tgbot.handlers.user import register_user
from tgbot.handlers.register import register_register_menu
from tgbot.handlers.common import register_common
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.services.Base import Base

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


logger = logging.getLogger(__name__)
def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(DomkomFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_domkom(dp)
    register_user(dp)
    register_common(dp)
    register_register_menu(dp)




async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    engine = create_async_engine(
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.database}",
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    bot["db"] = async_sessionmaker
    bot['config'] = config
    bot['logger'] = logger

    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

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