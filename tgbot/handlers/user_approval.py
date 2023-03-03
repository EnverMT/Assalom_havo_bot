from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import update, delete

import tgbot.models.models as models
from tgbot.misc.states import UserApprovalState
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
        text += f"Address: {address[0].house}/{address[0].apartment}"
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
        for p in phones:
            text += f"Tel: {p.numbers}\n"
    if addresses:
        for addr in addresses:
            text += f"Address: {addr.house}/{addr.apartment}\n"

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