from typing import List, Union


from aiogram.types import Message
from sqlalchemy import select

from tgbot.config import Config
from tgbot.models.models import Domkom
from tgbot.config import load_config


from aiogram.filters import Filter
class isUserHasRole(Filter):
    def __init__(self, role: Union[str, list]) -> None:
        self.role = role
        self.config = load_config(".env")

    async def __call__(self, message: Message) -> bool:
        if 'admin' in self.role or 'admin' == self.role:
            return message.from_user.id in self.config.tg_bot.admin_ids

        if 'domkom' in self.role or 'domkom' == self.role:
            db_session = message.via_bot.get("db")
            sql = select(Domkom).where(Domkom.telegram_id == message.from_user.id)
            async with db_session() as session:
                result = await session.execute(sql)
                domkom_list: List[Domkom] = result.first()
                if domkom_list:
                    return True

        return False