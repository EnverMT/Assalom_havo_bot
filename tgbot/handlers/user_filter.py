import re
from typing import List

import aiogram.utils.markdown
from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy import select

from tgbot.keyboards.inline import ListOfApprovedUsersMenu
from tgbot.misc.states import UserListState
from tgbot.models import models
from tgbot.services.DbCommands import DbCommands

db = DbCommands()


async def list_of_approved_users(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await state.reset_state()
    await UserListState.Menu.set()

    await call.answer(text="Выберите вид поиска")
    await call.bot.send_message(chat_id=call.from_user.id,
                                text="Выберите вид поиска",
                                reply_markup=ListOfApprovedUsersMenu)


async def list_of_approved_users_by_phone(call: types.CallbackQuery, state: FSMContext):
    await UserListState.FilterByPhone.set()
    await call.message.edit_reply_markup()
    await call.answer(text="list_of_approved_users_by_house")
    await call.bot.send_message(chat_id=call.from_user.id, text="Введите часть телефон номера:")


async def list_of_approved_users_by_phone_get_users(message: types.Message, state: FSMContext):
    if not message.text.isnumeric():
        await message.answer(text="Введите только цифру")
        return
    await state.reset_state()

    async with message.bot.get("db")() as session:
        users: List[models.User] = (await session.execute(select(models.User)
                                                          .join(models.Phone)
                                                          .where(models.Phone.numbers.contains(message.text)))) \
            .scalars().all()
    await list_of_approved_users_return_user_list(message=message, state=state, users=users)


async def list_of_approved_users_by_house(call: types.CallbackQuery, state: FSMContext):
    await UserListState.FilterByHouse.set()
    await call.message.edit_reply_markup()
    await call.answer(text="Фильтр по домам")
    await call.bot.send_message(chat_id=call.from_user.id,
                                text="Введите номер дома и квартиры(В формате 44-12) или только дома(44):")


async def list_of_approved_users_by_house_get_users(message: types.Message, state: FSMContext):
    if re.match(r"[0-9]+-[0-9]+", message.text):
        arr = message.text.split("-")
        house_num = int(arr[0])
        apartment_num = int(arr[1])
        async with message.bot.get("db")() as session:
            users: models.User = (await session.execute(select(models.User)
                                                        .join(models.Propiska)
                                                        .join(models.Address)
                                                        .where(models.Address.house == house_num)
                                                        .where(models.Address.apartment == apartment_num)
                                                        )).scalars().all()
    elif re.match(r"[0-9]+", message.text):
        house_num = int(message.text)
        async with message.bot.get("db")() as session:
            users: models.User = (await session.execute(select(models.User)
                                                        .join(models.Propiska)
                                                        .join(models.Address)
                                                        .where(models.Address.house == house_num)
                                                        )).scalars().all()
    else:
        await message.answer(text="Некорректный формат адреса дома")
        return
    if not users:
        await message.answer(text="Нет зарегистрированных жителей этого дома")
        return

    await state.reset_state()
    await list_of_approved_users_return_user_list(message=message, state=state, users=users)


async def list_of_approved_users_by_name(call: types.CallbackQuery, state: FSMContext):
    await UserListState.FilterByName.set()
    await call.message.edit_reply_markup()
    await call.answer(text="list_of_approved_users_by_house")
    await call.bot.send_message(chat_id=call.from_user.id, text="Введите часть имени:")


async def list_of_approved_users_by_name_get_users(message: types.Message, state: FSMContext):
    name_part = aiogram.utils.markdown.quote_html(message.text)
    await state.reset_state()

    async with message.bot.get("db")() as session:
        users: List[models.User] = (await session.execute(select(models.User)
                                                          .where(models.User.fio.contains(name_part) |
                                                                 models.User.full_name.contains(name_part) |
                                                                 models.User.username.contains(name_part)))) \
            .scalars().all()

    await list_of_approved_users_return_user_list(message=message, state=state, users=users)


async def list_of_approved_users_return_user_list(message: types.Message, state: FSMContext, users: List[models.User]):
    for user in users:
        addr: List[models.Address] = await user.get_addresses(call=message)
        phones = await user.get_phones(call=message)
        text = f"Ник: {user.full_name}\n"
        text += f"Имя: {user.fio}\n"
        text += f"username: {user.username}\n\n"
        for a in addr:
            text += f"Address: {a.house}/{a.apartment}\n"
        text += "\n"
        for p in phones:
            text += f"Tel: {p.numbers}\n"

        await message.answer(text=text)


def register_user_filter(dp: Dispatcher):
    dp.register_callback_query_handler(list_of_approved_users_by_phone,
                                       state=UserListState.Menu,
                                       text="list_of_approved_users_by_phone")
    dp.register_callback_query_handler(list_of_approved_users_by_house,
                                       state=UserListState.Menu,
                                       text="list_of_approved_users_by_house")

    dp.register_callback_query_handler(list_of_approved_users_by_name,
                                       state=UserListState.Menu,
                                       text="list_of_approved_users_by_name")

    dp.register_message_handler(list_of_approved_users_by_phone_get_users,
                                state=UserListState.FilterByPhone)
    dp.register_message_handler(list_of_approved_users_by_name_get_users,
                                state=UserListState.FilterByName)
    dp.register_message_handler(list_of_approved_users_by_house_get_users,
                                state=UserListState.FilterByHouse)