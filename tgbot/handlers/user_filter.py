import re
from typing import List

import aiogram.utils.markdown
from aiogram import Dispatcher, types, Router, enums, F, html
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot import bot
from tgbot.filters.userFilter import isUserHasRole
from tgbot.keyboards.inline import ListOfApprovedUsersMenu
from tgbot.misc.states import UserListState
from tgbot.models import *
from tgbot.services.DbCommands import DbCommands

db = DbCommands()

router = Router()
router.message.filter(F.chat.type == enums.ChatType.PRIVATE)
router.message.filter(isUserHasRole(['admin', 'domkom']))


@router.callback_query(F.data == "list_of_approved_users")
async def list_of_approved_users(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(UserListState.Menu)

    await call.answer(text="Выберите вид поиска")
    await bot.send_message(chat_id=call.from_user.id,
                           text="Выберите вид поиска",
                           reply_markup=ListOfApprovedUsersMenu)


@router.callback_query(UserListState.Menu, F.data == "list_of_approved_users_by_phone")
async def list_of_approved_users_by_phone(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserListState.FilterByPhone)
    await call.message.edit_reply_markup()
    await call.answer(text="Введите часть телефон номера:")
    await bot.send_message(chat_id=call.from_user.id, text="Введите часть телефон номера:")


@router.message(UserListState.FilterByPhone)
async def list_of_approved_users_by_phone_get_users(message: types.Message, state: FSMContext, session: AsyncSession):
    if not message.text.isnumeric():
        await message.answer(text="Введите только цифру")
        return
    await state.clear()

    users: List[User] = (await session.execute(select(User)
                                               .join(Phone)
                                               .where(Phone.numbers.contains(message.text)))) \
        .scalars().all()
    await list_of_approved_users_return_user_list(message=message, users=users, session=session)


@router.callback_query(UserListState.Menu, F.data == "list_of_approved_users_by_house")
async def list_of_approved_users_by_house(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserListState.FilterByHouse)
    await call.message.edit_reply_markup()
    await call.answer(text="Фильтр по домам")
    await bot.send_message(chat_id=call.from_user.id,
                           text="Введите номер дома и квартиры(В формате 44-12) или только дома(44):")


@router.message(UserListState.FilterByHouse)
async def list_of_approved_users_by_house_get_users(message: types.Message, state: FSMContext, session: AsyncSession):
    if re.match(r"[0-9]+-[0-9]+", message.text):
        arr = message.text.split("-")
        house_num = int(arr[0])
        apartment_num = int(arr[1])

        users: User = (await session.execute(select(User)
                                             .join(Propiska)
                                             .join(Address)
                                             .where(Address.house == house_num)
                                             .where(Address.apartment == apartment_num)
                                             )).scalars().all()
    elif re.match(r"[0-9]+", message.text):
        house_num = int(message.text)
        users: User = (await session.execute(select(User)
                                             .join(Propiska)
                                             .join(Address)
                                             .where(Address.house == house_num)
                                             )).scalars().all()
    else:
        await message.answer(text="Некорректный формат адреса дома")
        return
    if not users:
        await message.answer(text="Нет зарегистрированных жителей этого дома")
        return

    await state.clear()
    await list_of_approved_users_return_user_list(message=message, users=users, session=session)

@router.callback_query(UserListState.Menu, F.data == "list_of_approved_users_by_name")
async def list_of_approved_users_by_name(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserListState.FilterByName)
    await call.message.edit_reply_markup()
    await call.answer(text="Введите часть имени:")
    await bot.send_message(chat_id=call.from_user.id, text="Введите часть имени:")


@router.message(UserListState.FilterByName)
async def list_of_approved_users_by_name_get_users(message: types.Message, state: FSMContext, session:AsyncSession):
    name_part = html.quote(message.text)
    await state.clear()

    users: List[User] = (await session.execute(select(User)
                                               .where(User.fio.contains(name_part) |
                                                      User.full_name.contains(name_part) |
                                                      User.username.contains(name_part)))) \
        .scalars().all()

    await list_of_approved_users_return_user_list(message=message, users=users, session=session)


async def list_of_approved_users_return_user_list(message: types.Message, users: List[User], session: AsyncSession):
    for user in users:
        addr: List[Address] = await user.get_addresses(session=session)
        phones = await user.get_phones(session=session)
        text = f"Ник: {user.full_name}\n"
        text += f"Имя: {user.fio}\n"
        text += f"username: {user.username}\n\n"
        for a in addr:
            text += f"Address: {a.house}/{a.apartment}\n"
        text += "\n"
        for p in phones:
            text += f"Tel: {p.numbers}\n"

        await message.answer(text=text)
