from typing import List, Tuple

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, update, delete, insert

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
        address = await user.get_addresses(call=call)
        text = f"Ник: {user.full_name}\t  "
        text += f"Address: {address[0][0].house}/{address[0][0].apartment}"
        inline_user_keyboard.add(InlineKeyboardButton(text=text, callback_data=user.id))
    await call.bot.send_message(chat_id=call.from_user.id, text="List of waiting approval users",
                                reply_markup=inline_user_keyboard)
    await UserApprovalState.ListOfWaitingApprovalUsers.set()


async def waiting_approval_user(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    user: models.User = await db.select_user(call=call, user_id=int(call.data))
    text = f"Ник: {user.full_name}\n"
    text += f"Имя: {user.fio}\n"

    phones = await user.get_phones(call=call)
    addresses = await user.get_addresses(call=call)

    if phones:
        for phone_tuple in phones:
            text += f"Tel: {phone_tuple[0].numbers}\n"
    if addresses:
        for addr_tuple in addresses:
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
    user_id = int(user_data['user_id'])
    await call.message.edit_reply_markup()

    if call.data == "Approve":
        sql = update(models.User).values(isApproved=True, whoApproved=call.from_user.id).where(
            models.User.id == user_id)
        async with db_session() as session:
            await session.execute(sql)
            await session.commit()

        await call.bot.send_message(chat_id=call.from_user.id, text="Approved")
        user: models.User = await db.select_user(call=call, user_id=user_id)
        await call.bot.send_message(chat_id=user.telegram_id, text="Ваша заявка была одобрена. Нажмите /start.")
    else:
        await call.answer(text="Заявка отменена")

        sql = delete(models.User).where(models.User.id == user_id)
        async with db_session() as session:
            await session.execute(sql)
            await session.commit()
        await state.reset_state()
        await state.finish()


async def info_about_me(call: types.CallbackQuery):
    await call.message.edit_reply_markup()

    user = await db.select_current_user(call)
    text = f"Ник: {user.full_name}\n"
    text += f"Имя: {user.fio}\n"

    addresses = await user.get_addresses(call=call)
    phones = await user.get_phones(call=call)
    for p in phones:
        text += f"Tel: {p[0].numbers}\n"
    for a in addresses:
        text += f"Address: {a[0].house}/{a[0].apartment}\n"
        text += f"Газ л.с. - <code>{a[0].gaz_litsevoy_schet}</code>\n"
        text += f"Размер квартиры - {a[0].room_size}\n"
        text += f"Номер кадастра - <code>{a[0].kadastr_number}</code>\n"
        text += f"Номер счетчика газа - {a[0].gaz_schetchik_nomer}\n"
        text += f"Мусор л.с. - <code>{a[0].musor_ls}</code>\n"

    await call.bot.send_message(chat_id=call.from_user.id, text=f"{text}")


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


def register_common(dp: Dispatcher):
    dp.register_callback_query_handler(info_about_me, state='*', text_contains="info_aboutme")
    dp.register_message_handler(cancel, state='*', commands=['cancel'])