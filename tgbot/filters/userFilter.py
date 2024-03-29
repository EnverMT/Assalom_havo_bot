from typing import List, Union

from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy import select

import bot
from tgbot.config import load_config
from tgbot.models import *
from tgbot.services.DbCommands import DbCommands

db = DbCommands()

class isUserHasRole(Filter):
    def __init__(self, role: Union[str, list]) -> None:
        self.role = role
        self.config = load_config(".env")

    async def __call__(self, message: Message) -> bool:
        filterCheckResult = False
        if 'admin' in self.role or 'admin' == self.role:
            result = message.from_user.id in self.config.tg_bot.admin_ids
            if result:
                filterCheckResult = True

        if filterCheckResult:
            return True

        if 'domkom' in self.role or 'domkom' == self.role:
            db_session = bot.session_pool
            sql = select(Domkom).where(Domkom.telegram_id == message.from_user.id)
            async with db_session() as session:
                result = await session.execute(sql)
                domkom_list: List[Domkom] = result.first()
                if domkom_list:
                    filterCheckResult = True

        return filterCheckResult
