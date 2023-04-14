from typing import List, Tuple

from aiogram import types, Router, F, enums
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot import bot
from tgbot.filters.userFilter import isUserHasRole
from tgbot.misc.states import DomkomControlState, AdminState
from tgbot.models import *
from tgbot.services.DbCommands import DbCommands

db = DbCommands()

router = Router()
router.message.filter(F.chat.type == enums.ChatType.PRIVATE)
router.message.filter(isUserHasRole(['admin']))


@router.callback_query(AdminState.Menu, F.data == 'list_of_domkoms')
async def list_of_domkoms(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(DomkomControlState.ListOfDomkoms)
    sql = select(User, Phone) \
        .join(Domkom, User.id == Domkom.user_id) \
        .join(Phone, User.id == Phone.user_id)

    res = await session.execute(sql)
    domkoms: List[Tuple[User]] = res.all()
    if not domkoms:
        await bot.send_message(chat_id=call.from_user.id, text="Нет домкомов")
        await call.answer(text="Нет домкомов")
        return

    builder = InlineKeyboardBuilder()
    for user, phone in domkoms:
        builder.add(types.InlineKeyboardButton(text=f"{user.full_name} / {phone.numbers}", callback_data=user.id))
    await bot.send_message(chat_id=call.from_user.id, text="Домкомы:", reply_markup=builder.as_markup())
    await call.answer(text="Домкомы")


@router.callback_query(AdminState.Menu, F.data == "add_new_domkom")
async def add_new_domkom(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(DomkomControlState.AddNewDomkom)
    text = "Введите часть телефон номера:"
    await bot.send_message(chat_id=call.from_user.id, text=text)
    await call.answer(text=text)


@router.message(DomkomControlState.AddNewDomkom)
async def add_new_domkom_filtered(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.set_state(DomkomControlState.AddNewDomkomFiltered)
    users: List[User] = (await session.execute(select(User).join(Phone).where(Phone.numbers.contains(message.text)))) \
        .scalars().all()

    if not users:
        await bot.send_message(chat_id=message.from_user.id, text="Нет кандидатов")
        return

    users_list_buttons = InlineKeyboardBuilder()
    for user in users:
        is_domkom = await user.is_domkom(session=session)
        if is_domkom:
            continue
        phones = await user.get_phones(session=session)
        users_list_buttons.add(
            types.InlineKeyboardButton(text=f"{user.full_name} / {phones[0].numbers}", callback_data=user.id))
    await bot.send_message(chat_id=message.from_user.id, text="Кандидаты:", reply_markup=users_list_buttons.as_markup())


@router.callback_query(DomkomControlState.AddNewDomkomFiltered)
async def assign_new_domkom(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = int(call.data)
    user = await db.select_user(user_id=user_id, session=session)
    is_domkom = await user.is_domkom(session=session, user_id=user_id)
    if is_domkom:
        await bot.send_message(chat_id=call.from_user.id, text=f"Alrady domkom: {user.full_name}")
        return

    sql = insert(Domkom).values(user_id=int(user.id),
                                telegram_id=int(user.telegram_id),
                                whoAssigned=int(call.from_user.id))
    await session.execute(sql)
    await session.commit()

    await bot.send_message(chat_id=call.from_user.id, text=f"Assigned: {user.full_name}")
    await call.answer(text=f"Assigned: {user.full_name}")
