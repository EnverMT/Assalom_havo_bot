import re
from typing import List, Tuple

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, insert, delete

import tgbot.misc.states as states
from tgbot.models import models
from tgbot.services.DbCommands import DbCommands

db = DbCommands()


async def auto_info_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await states.AutoInfoState.Menu.set()
    user = await db.select_current_user(call)

    auto_menu = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Найти владелца авто по номеру", callback_data="auto_find_owner_by_number")],
            [InlineKeyboardButton(text="Добавить автомобиль", callback_data="auto_add")]
        ]
    )

    if await user.get_autos(call=call):
        auto_menu.add(InlineKeyboardButton(text="Мои автомобилы", callback_data="auto_list_my_cars"))
        auto_menu.add(InlineKeyboardButton(text="Удалить автомобиль", callback_data="auto_delete"))

    await call.bot.send_message(chat_id=call.from_user.id, text="Автомобиль", reply_markup=auto_menu)


async def auto_list_my_cars(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await state.finish()
    await state.reset_state()

    user = await db.select_current_user(call)
    autos = await user.get_autos(call=call)

    await call.bot.send_message(chat_id=call.from_user.id, text="Список моих машин:")
    for auto in autos:
        text = f"Номер машины: {auto.number}"
        await call.bot.send_message(chat_id=call.from_user.id, text=text)


async def auto_find_owner_by_number(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await states.AutoInfoState.auto_find_owner_by_number.set()
    await call.bot.send_message(chat_id=call.from_user.id, text="Введите часть номера для поиска:")


async def auto_find_owner_by_number_result(message: types.Message, state: FSMContext):
    if not re.match(r"[0-9a-zA-Z]+", message.text):
        await message.bot.send_message(chat_id=message.from_user.id, text="Используйте только латинские буквы и цифры")
        return

    async with message.bot.get("db")() as session:
        result: List[Tuple[models.User, models.Auto]] = (await session.execute(
            select(models.User, models.Auto).join(models.Auto, models.User.id == models.Auto.user_id)
            .where(models.Auto.number.ilike(f"%{message.text}%")))) \
            .all()

        await message.bot.send_message(chat_id=message.from_user.id, text="Список владельцев: \n\n")
        for user, auto in result:
            text = f"Имя: {user.fio}\n\n"

            phones = await user.get_phones(call=message)
            for phone in phones:
                text += f"Телефон: {phone.numbers}\n"

            text += f"\nНомер машины: {auto.number}"

            await message.bot.send_message(chat_id=message.from_user.id, text=text)
    await state.finish()


async def auto_add(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await states.AutoInfoState.AutoAdd.set()
    await call.bot.send_message(chat_id=call.from_user.id, text="Введите номер вашей машины в формате 01-A123BC.")
    await call.bot.send_message(chat_id=call.from_user.id, text="Допускается только цифры и прописные латинские буквы")


async def auto_add_number_check(message: types.Message, state: FSMContext):
    # Не допускается использование буквы I в номерах машины
    if not re.match(r"[0-9]{2}-[0-9A-HJ-Z]{6}", message.text):
        await message.bot.send_message(chat_id=message.from_user.id, text="Введенный номер не соответствует формату")
        return

    async with message.bot.get("db")() as session:
        user = await db.select_current_user(message)
        try:
            await session.execute(insert(models.Auto).values(user_id=user.id,
                                                             number=message.text))
            await session.commit()
            await message.answer(text="Ваш авто добавлена в список")
        except Exception as ex:
            await message.answer(text=f"Ошибка!!!")

    await state.finish()


async def auto_delete(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await states.AutoInfoState.AutoDelete.set()

    user = await db.select_current_user(call)
    cars_list = InlineKeyboardMarkup()
    cars = await user.get_autos(call=call)

    for car in cars:
        cars_list.add(InlineKeyboardButton(text=f"Номер: {car.number}",
                                           callback_data=car.id))
    await call.bot.send_message(chat_id=call.from_user.id,
                                text="Выберите машину для удаления",
                                reply_markup=cars_list)


async def auto_delete_result(call: types.CallbackQuery, state: FSMContext):
    async with call.bot.get("db")() as session:
        try:
            await session.execute(delete(models.Auto).where(models.Auto.id == int(call.data)))
            await session.commit()
            await call.answer(text="Удалено")
        except Exception as ex:
            await call.answer(text="Ошибка!!!")
        finally:
            await call.message.edit_reply_markup()
    await state.finish()


def register_auto(dp: Dispatcher):
    dp.register_callback_query_handler(auto_info_menu, state='*', text="auto_info_menu")
    dp.register_callback_query_handler(auto_list_my_cars, state=states.AutoInfoState.Menu, text="auto_list_my_cars")
    dp.register_callback_query_handler(auto_find_owner_by_number, state=states.AutoInfoState.Menu,
                                       text="auto_find_owner_by_number")
    dp.register_message_handler(auto_find_owner_by_number_result, state=states.AutoInfoState.auto_find_owner_by_number)

    dp.register_callback_query_handler(auto_add, state=states.AutoInfoState.Menu, text="auto_add")
    dp.register_message_handler(auto_add_number_check, state=states.AutoInfoState.AutoAdd)

    dp.register_callback_query_handler(auto_delete, state=states.AutoInfoState.Menu, text="auto_delete")
    dp.register_callback_query_handler(auto_delete_result, state=states.AutoInfoState.AutoDelete)