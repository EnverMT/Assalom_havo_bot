from typing import List, Tuple

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, insert

import tgbot.models.models as models
from tgbot.misc.states import DomkomControlState
from tgbot.services.DbCommands import DbCommands

db = DbCommands()


async def list_of_domkoms(call: types.CallbackQuery, state: FSMContext):
    await DomkomControlState.ListOfDomkoms.set()
    db_session = call.bot.get("db")
    sql = select(models.User, models.Phone) \
        .join(models.Domkom, models.User.id == models.Domkom.user_id) \
        .join(models.Phone, models.User.id == models.Phone.user_id)

    async with db_session() as session:
        res = await session.execute(sql)
        domkoms: List[Tuple[models.User]] = res.all()
        if not domkoms:
            await call.bot.send_message(chat_id=call.from_user.id, text="Нет домкомов")

        domkoms_list_buttons = InlineKeyboardMarkup()
        for user, phone in domkoms:
            domkoms_list_buttons.add(
                InlineKeyboardButton(text=f"{user.full_name} / {phone.numbers}", callback_data=user.id))
        await call.bot.send_message(chat_id=call.from_user.id, text="Домкомы:", reply_markup=domkoms_list_buttons)


async def add_new_domkom(call: types.CallbackQuery, state: FSMContext):
    await DomkomControlState.AddNewDomkom.set()
    await call.bot.send_message(chat_id=call.from_user.id, text="Выберите кандидата на домкомы:")
    sql = select(models.User, models.Phone).join(models.Phone, models.User.id == models.Phone.user_id)
    db_session = call.bot.get("db")
    async with db_session() as session:
        res = await session.execute(sql)
        users: List[Tuple[models.User]] = res.all()
        if not users:
            await call.bot.send_message(chat_id=call.from_user.id, text="Нет кандидатов")

        users_list_buttons = InlineKeyboardMarkup()
        for user, phone in users:
            is_domkom = await user.is_domkom(call=call)
            if is_domkom:
                continue
            users_list_buttons.add(
                InlineKeyboardButton(text=f"{user.full_name} / {phone.numbers}", callback_data=user.id))
        await call.bot.send_message(chat_id=call.from_user.id, text="Кандидаты:", reply_markup=users_list_buttons)


async def assign_new_domkom(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data)
    user = await db.select_user(call=call, user_id=user_id)
    is_domkom = await user.is_domkom(call=call, user_id=user_id)
    if is_domkom:
        await call.bot.send_message(chat_id=call.from_user.id, text=f"Alrady domkom: {user.full_name}")
        return

    sql = insert(models.Domkom).values(user_id=int(user.id),
                                       telegram_id=int(user.telegram_id),
                                       whoAssigned=int(call.from_user.id))
    db_session = call.bot.get("db")
    async with db_session() as session:
        await session.execute(sql)
        await session.commit()

    await call.bot.send_message(chat_id=call.from_user.id, text=f"Assigned: {user.full_name}")