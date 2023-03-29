from typing import List, Tuple

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, insert

import tgbot.models.models as models
from tgbot.misc.states import DomkomControlState, AdminState
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
    await call.bot.send_message(chat_id=call.from_user.id, text="Введите часть телефон номера:")


async def add_new_domkom_filtered(message: types.Message):
    await DomkomControlState.AddNewDomkomFiltered.set()
    async with message.bot.get("db")() as session:
        users: List[models.User] = (await session.execute(select(models.User)
                                                          .join(models.Phone)
                                                          .where(models.Phone.numbers.contains(message.text)))) \
            .scalars().all()

    if not users:
        await message.bot.send_message(chat_id=message.from_user.id, text="Нет кандидатов")

    users_list_buttons = InlineKeyboardMarkup()
    for user in users:
        is_domkom = await user.is_domkom(call=message)
        if is_domkom:
            continue
        phones = await user.get_phones(call=message)
        users_list_buttons.add(
            InlineKeyboardButton(text=f"{user.full_name} / {phones[0].numbers}", callback_data=user.id))
    await message.bot.send_message(chat_id=message.from_user.id, text="Кандидаты:", reply_markup=users_list_buttons)


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


def register_domkom_approval(dp: Dispatcher):
    dp.register_callback_query_handler(list_of_domkoms,
                                       state=AdminState.Menu,
                                       text_contains="list_of_domkoms",
                                       is_admin=True)

    dp.register_callback_query_handler(add_new_domkom,
                                       state=AdminState.Menu,
                                       text_contains="add_new_domkom")

    dp.register_message_handler(add_new_domkom_filtered,
                                state=DomkomControlState.AddNewDomkom, )

    dp.register_callback_query_handler(assign_new_domkom,
                                       state=DomkomControlState.AddNewDomkomFiltered)