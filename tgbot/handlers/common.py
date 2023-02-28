from typing import List, Tuple

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, update, delete

import tgbot.models.models as models
from tgbot.misc.states import UserApprovalState, DomkomControlState
from tgbot.services.DbCommands import DbCommands

db = DbCommands()


async def list_of_waiting_approval_users(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    users = await db.get_list_of_waiting_approval_users(call=call)
    inline_user_keyboard = InlineKeyboardMarkup(row_width=1)
    if not users:
        await call.bot.send_message(chat_id=call.from_user.id, text="No users waiting")
        return

    for user, phone in users:
        text = f"Имя: {user.full_name}\t"
        text += f"Phone: {phone.numbers}"
        inline_user_keyboard.add(InlineKeyboardButton(text=text, callback_data=user.id))
    await call.bot.send_message(chat_id=call.from_user.id, text="List of waiting approval users",
                                reply_markup=inline_user_keyboard)
    await UserApprovalState.ListOfWaitingApprovalUsers.set()


async def waiting_approval_user(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    user: models.User = await db.select_user(call=call, user_id=int(call.data))
    text = f"Name: {user.full_name}\n"

    db_session = call.bot.get("db")
    sql_phone = select(models.Phone).where(models.Phone.user_id == int(user.id))
    sql_addresses = select(models.Address).where(models.Address.user_id == int(user.id))

    async with db_session() as session:
        phones = await session.execute(sql_phone)
        addresses = await session.execute(sql_addresses)
        phone_list: List[Tuple[models.Phone]] = phones.all()
        addresses_list: List[Tuple[models.Address]] = addresses.all()
        if phone_list:
            for phone_tuple in phone_list:
                text += f"Tel: {phone_tuple[0].numbers}\n"
        if addresses_list:
            for addr_tuple in addresses_list:
                text += f"Address: {addr_tuple[0].house}/{addr_tuple[0].apartment}\n"

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text="Принять", callback_data="Approve"))
    keyboard.add(InlineKeyboardButton(text="Отказать", callback_data="Deny"))

    await UserApprovalState.WaitingApprovalUser.set()  # State
    await state.update_data(user_id=int(user.id))
    await call.bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard)


async def approve_user(call: types.CallbackQuery, state: FSMContext):
    db_session = call.bot.get("db")
    user_data = await state.get_data()
    user_id = user_data['user_id']

    if call.data == "Approve":
        sql = update(models.User).values(isApproved=True, whoApproved=call.from_user.id).where(
            models.User.id == user_id)
        async with db_session() as session:
            await session.execute(sql)
            await session.commit()

        await call.message.edit_reply_markup()
        await call.bot.send_message(chat_id=call.from_user.id, text="Approved")
        user: models.User = await db.select_user(call=call, user_id=user_id)
        await call.bot.send_message(chat_id=user.telegram_id, text="Ваша заявка была одобрена")
    else:
        await state.reset_state()
        await state.finish()
        sql = delete(models.User).where(models.User.id == user_id)
        async with db_session() as session:
            await session.execute(sql)
            await session.commit()
        await call.bot.send_message(chat_id=call.from_user.id, text="Denied")


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
        domkoms_list_buttons.add(InlineKeyboardButton(text="Добавить нового домкома", callback_data="add_new_domkom"))
        for user, phone in domkoms:
            domkoms_list_buttons.add(
                InlineKeyboardButton(text=f"{user.full_name} / {phone.numbers}", callback_data=user.id))
        await call.bot.send_message(chat_id=call.from_user.id, text="Домкомы:", reply_markup=domkoms_list_buttons)


async def cancel(message: types.Message, state: FSMContext):
    """
      Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())