import re
from typing import List, Tuple

from aiogram import types, Dispatcher, Router, F, enums
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot import bot
from tgbot.misc.states import AutoInfoState
from tgbot.models import *
from tgbot.services.DbCommands import DbCommands

db = DbCommands()
router = Router()
router.message.filter(F.chat.type == enums.ChatType.PRIVATE)


@router.callback_query(F.data == "auto_info_menu")
async def auto_info_menu(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.message.edit_reply_markup()
    await state.set_state(AutoInfoState.Menu)
    user = await db.select_current_user(call, session=session)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Найти владелца авто по номеру", callback_data="auto_find_owner_by_number"))
    builder.row(InlineKeyboardButton(text="Добавить автомобиль", callback_data="auto_add"))

    if await user.get_autos(session=session):
        builder.row(InlineKeyboardButton(text="Мои автомобилы", callback_data="auto_list_my_cars"))
        builder.row(InlineKeyboardButton(text="Удалить автомобиль", callback_data="auto_delete"))

    await bot.send_message(chat_id=call.from_user.id, text="Автомобиль", reply_markup=builder.as_markup())


@router.callback_query(AutoInfoState.Menu, F.data == "auto_list_my_cars")
async def auto_list_my_cars(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.message.edit_reply_markup()
    await state.clear()

    user = await db.select_current_user(message=call, session=session)
    autos = await user.get_autos(session=session)

    await bot.send_message(chat_id=call.from_user.id, text="Список моих машин:")
    for auto in autos:
        text = f"Номер машины: {auto.number}"
        await bot.send_message(chat_id=call.from_user.id, text=text)
        await call.answer(text="Машины")


@router.callback_query(AutoInfoState.Menu, F.data == "auto_find_owner_by_number")
async def auto_find_owner_by_number(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await state.set_state(AutoInfoState.auto_find_owner_by_number)
    text = "Введите часть номера для поиска:"
    await bot.send_message(chat_id=call.from_user.id, text=text)
    await call.answer(text=text)


@router.message(AutoInfoState.auto_find_owner_by_number)
async def auto_find_owner_by_number_result(message: types.Message, state: FSMContext, session: AsyncSession):
    if not re.match(r"[0-9a-zA-Z]+", message.text):
        await bot.send_message(chat_id=message.from_user.id, text="Используйте только латинские буквы и цифры")
        return

    result: List[Tuple[User, Auto]] = (await session.execute(
        select(User, Auto).join(Auto, User.id == Auto.user_id).where(Auto.number.ilike(f"%{message.text}%")))) \
        .all()

    await bot.send_message(chat_id=message.from_user.id, text="Список владельцев: \n\n")
    for user, auto in result:
        text = f"Имя: {user.fio}\n\n"

        phones = await user.get_phones(session=session)
        for phone in phones:
            text += f"Телефон: {phone.numbers}\n"

        text += f"\nНомер машины: {auto.number}"

        await bot.send_message(chat_id=message.from_user.id, text=text)
    await state.clear()


@router.callback_query(AutoInfoState.Menu, F.data == "auto_add")
async def auto_add(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await state.set_state(AutoInfoState.AutoAdd)
    await bot.send_message(chat_id=call.from_user.id, text="Введите номер вашей машины в формате 01-A123BC.")
    await bot.send_message(chat_id=call.from_user.id, text="Допускается только цифры и прописные латинские буквы")
    await call.answer(text="Добавление авто")


@router.message(AutoInfoState.AutoAdd)
async def auto_add_number_check(message: types.Message, state: FSMContext, session: AsyncSession):
    # Не допускается использование буквы I в номерах машины
    if not re.match(r"[0-9]{2}-[0-9A-HJ-Z]{6}", message.text):
        await bot.send_message(chat_id=message.from_user.id, text="Введенный номер не соответствует формату")
        return

    user = await db.select_current_user(message=message, session=session)
    try:
        await session.execute(insert(Auto).values(user_id=user.id,
                                                  number=message.text))
        await session.commit()
        await message.answer(text="Ваш авто добавлена в список")
    except Exception as ex:
        await message.answer(text=f"Ошибка!!!")

    await state.clear()


@router.callback_query(AutoInfoState.Menu, F.data == "auto_delete")
async def auto_delete(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.message.edit_reply_markup()
    await state.set_state(AutoInfoState.AutoDelete)

    user = await db.select_current_user(message=call, session=session)
    cars = await user.get_autos(session=session)

    cars_list = InlineKeyboardBuilder()
    for car in cars:
        cars_list.row(InlineKeyboardButton(text=f"Номер: {car.number}",
                                           callback_data=car.id))
    await bot.send_message(chat_id=call.from_user.id,
                           text="Выберите машину для удаления",
                           reply_markup=cars_list.as_markup())


@router.callback_query(AutoInfoState.AutoDelete)
async def auto_delete_result(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    try:
        await session.execute(delete(Auto).where(Auto.id == int(call.data)))
        await session.commit()
        await call.answer(text="Удалено")
    except Exception as ex:
        await call.answer(text="Ошибка!!!")
    finally:
        await call.message.edit_reply_markup()
    await state.clear()
