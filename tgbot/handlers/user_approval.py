from aiogram import types, Router, F, enums
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot import bot
from tgbot.filters.userFilter import isUserHasRole
from tgbot.misc.states import UserApprovalState
from tgbot.models import *
from tgbot.services.DbCommands import DbCommands

db = DbCommands()

router = Router()
router.message.filter(F.chat.type == enums.ChatType.PRIVATE)
router.message.filter(isUserHasRole(['admin', 'domkom']))


@router.callback_query(F.data == "list_of_waiting_approval_users")
async def list_of_waiting_approval_users(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.message.edit_reply_markup()
    users = await db.get_list_of_waiting_approval_users(session=session)

    inline_user_keyboard = InlineKeyboardBuilder()
    if not users:
        await bot.send_message(chat_id=call.from_user.id, text="No users waiting")
        return

    for user, phone in users:
        address = await user.get_addresses(session=session)
        text = f"Ник: {user.full_name}\t  "
        text += f"Address: {address[0].house}/{address[0].apartment}"
        inline_user_keyboard.row(InlineKeyboardButton(text=text, callback_data=user.id))
    await bot.send_message(chat_id=call.from_user.id, text="List of waiting approval users",
                           reply_markup=inline_user_keyboard.as_markup())
    await state.set_state(UserApprovalState.ListOfWaitingApprovalUsers)


@router.callback_query(UserApprovalState.ListOfWaitingApprovalUsers)
async def waiting_approval_user(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.message.edit_reply_markup()
    user: User = await db.select_user(session=session, user_id=int(call.data))
    text = f"Ник: {user.full_name}\n"
    text += f"Имя: {user.fio}\n"

    phones = await user.get_phones(session=session)
    addresses = await user.get_addresses(session=session)

    if phones:
        for p in phones:
            text += f"Tel: {p.numbers}\n"
    if addresses:
        for addr in addresses:
            text += f"Address: {addr.house}/{addr.apartment}\n"

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Принять", callback_data="Approve"))
    keyboard.row(InlineKeyboardButton(text="Отказать", callback_data="Deny"))

    await state.set_state(UserApprovalState.WaitingApprovalUser)
    await state.update_data(user_id=int(user.id))
    await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard.as_markup())


@router.callback_query(UserApprovalState.WaitingApprovalUser)
async def approve_user(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    user_id = int(user_data['user_id'])
    await call.message.edit_reply_markup()

    if call.data == "Approve":
        try:
            sql = update(User).values(isApproved=True, whoApproved=call.from_user.id).where(
                User.id == user_id)
            await session.execute(sql)
            await session.commit()

            await bot.send_message(chat_id=call.from_user.id, text="Approved")
            await call.answer(text="Approved")
            user: User = await db.select_user(session=session, user_id=user_id)
            await bot.send_message(chat_id=user.telegram_id, text="Ваша заявка была одобрена. Нажмите /start.")
        except Exception as ex:
            await call.answer(text="Ошибка")
            return
    else:
        sql = delete(User).where(User.id == user_id)
        await session.execute(sql)
        await session.commit()

        await call.answer(text="Заявка отклонена")
        await state.clear()
