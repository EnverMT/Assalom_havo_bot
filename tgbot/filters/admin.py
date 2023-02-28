import typing
from typing import List

from aiogram.dispatcher.filters import BoundFilter
from sqlalchemy import select

from tgbot.config import Config
from tgbot.models.models import Domkom


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, obj):
        if self.is_admin is None:
            return False
        config: Config = obj.bot.get('config')
        return (obj.from_user.id in config.tg_bot.admin_ids) == self.is_admin


class DomkomFilter(BoundFilter):
    key = 'is_domkom'

    def __init__(self, is_domkom: typing.Optional[bool] = None):
        self.is_domkom = is_domkom

    async def check(self, obj):
        if self.is_domkom is None:
            return False

        db_session = obj.bot.get("db")
        sql = select(Domkom).where(Domkom.telegram_id == obj.from_user.id)
        async with db_session() as session:
            result = await session.execute(sql)
            domkom_list: List[Domkom] = result.first()
            if not domkom_list:
                return False
            return self.is_domkom is True