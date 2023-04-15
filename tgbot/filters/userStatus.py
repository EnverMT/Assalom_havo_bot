from typing import List, Union

from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy import select

import bot
from tgbot.config import load_config
from tgbot.models import *
from tgbot.services.DbCommands import DbCommands

db = DbCommands()

class userStatus(Filter):
    def __init__(self, role: Union[str, list]) -> None:
        self.role = role
        self.config = load_config(".env")

    async def __call__(self, message: Message) -> bool:
        if 'notApproved' in self.role or 'notApproved' == self.role:
            result = message.from_user.id in self.config.tg_bot.admin_ids
            if result:
                return False


            db_session = bot.session_pool
            sql = select(User).where(User.telegram_id == message.from_user.id, User.isApproved == True)
            async with db_session() as session:
                result = await session.execute(sql)
                isApproved: List[Domkom] = result.scalars().first()
                if not isApproved:
                    return True

        return False
