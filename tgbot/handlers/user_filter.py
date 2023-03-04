from typing import List

import aiogram.utils.markdown
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
    await call.bot.send_message(chat_id=call.from_user.id, text="Введите номер дома(В формате 44-12):")


async def list_of_approved_users_by_house_get_users(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if not message.text.isnumeric():
        await message.answer(text="Введите только цифру")
        return
    async with message.bot.get("db")() as session:
        house: models.Address = (await session.execute(select(models.Address)
                                                       .where(models.Address.house == int(message.text)))) \
            .scalars().all()
    if not house:
        await message.answer(text="Такой дом не существует в базе")
        return
    await state.update_data(house_number=house.house)

    if message.text != '*':
        if not message.text.isnumeric():
            await message.answer(text="Введите только цифру")
            return
        async with message.bot.get("db")() as session:
            apartment: models.Address = (await session.execute(select(models.Address)
                                                               .where(models.Address.apartment == int(message.text)))) \
                .scalars().all()
        if not apartment:
            await message.answer(text="Такой квартиры не существует в базе")
            return

    await state.reset_state()

    async with message.bot.get("db")() as session:
        users: List[models.User] = \
            (await session.execute(select(models.User)
                                   .join(models.Propiska)
                                   .join(models.Address)
                                   .where(models.Address.house == house &
                                          models.Address.apartment == apartment))) \
                .scalars().all()

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
