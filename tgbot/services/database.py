from gino.schema import GinoSchemaVisitor
import tgbot.config
from tgbot.models.models import User
from tgbot.services.db import db
from aiogram import types


class DBCommands:
    async def register_add_phone_number(self, phone_number):
        user = await User.query.where(User.user_id == types.User.get_current().id).gino.first()
        return await user.update(phone_number=phone_number).apply()

    async def register_add_fio(self, fio):
        user = await User.query.where(User.user_id == types.User.get_current().id).gino.first()
        return await user.update(fio=fio).apply()

    async def register_add_house_number(self, house_num):
        user = await User.query.where(User.user_id == types.User.get_current().id).gino.first()
        return await user.update(house_number=house_num).apply()

    async def register_add_apartment_number(self, num):
        user = await User.query.where(User.user_id == types.User.get_current().id).gino.first()
        return await user.update(apartment_number=num).apply()

    async def register_final(self):
        user = await User.query.where(User.user_id == types.User.get_current().id).gino.first()
        return await user.update(awaiting_register=True).apply()

    async def get_user(self, user_id) -> User:
        return await User.query.where(User.user_id == user_id).gino.first()



    async def add_new_user(self, referral=None) -> User:
        user = types.User.get_current()
        old_user = await self.get_user(user.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.user_id = user.id
        new_user.username = user.username
        new_user.full_name = user.full_name

        if referral:
            new_user.referral = int(referral)
        await new_user.create()
        return new_user


async def create_db(config: tgbot.config.Config):
    await db.set_bind(f'postgresql://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.database}')

    # Create tables
    db.gino: GinoSchemaVisitor

    # Alembic will handle DB structure
    # alembic revision -m "your migration description" --autogenerate --head head
    # alembic upgrade head
    # await db.gino.drop_all()
    # await db.gino.create_all()
