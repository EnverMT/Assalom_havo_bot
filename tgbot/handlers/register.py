from typing import List

from aiogram import types, html, Router, enums, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot import bot
from tgbot.misc.states import RegisterState
from tgbot.models import *
from tgbot.services.DbCommands import DbCommands

db = DbCommands()

router = Router()
router.message.filter(F.chat.type == enums.ChatType.PRIVATE)


@router.message(Command('register'))
async def check_register_status(message: types.Message, state: FSMContext, session: AsyncSession):
    user = await db.select_current_user(message=message, session=session)

    if not user:
        return

    if user.isApproved:
        await bot.send_message(chat_id=message.from_user.id, text=f"Вы уже прошли регистрацию {user.full_name}")
        return

    phones = await user.get_phones(session=session)
    if phones:
        await bot.send_message(chat_id=message.from_user.id, text="Ваша заявка под рассмотрением")
        return

    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Для продолжения регистрации, прошу написать вашу Фамилию и Имя {user.full_name}")
    await state.set_state(RegisterState.ReadyToRegister)


@router.message(RegisterState.ReadyToRegister)
async def register_get_fio(message: types.Message, state: FSMContext):
    await state.set_state(RegisterState.fio)
    await state.update_data(fio=html.quote(message.text))

    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="Ваш Контакт.", request_contact=True))

    await message.answer(text=f"Прошу предоставит ваш телефон Контакт.",
                         reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(RegisterState.fio, F.contact)
async def register_get_contact(message: types.Message, state: FSMContext):
    if (message.from_user.id != message.contact.user_id):
        await state.clear()  # TO DO: Ban such cheating users
        return
    await state.set_state(RegisterState.phone_number)
    await state.update_data(user_phone=message.contact.phone_number)
    await message.answer(f"Ввведите номер вашего дома: (Только цифрами)", reply_markup=types.ReplyKeyboardRemove())


@router.message(RegisterState.phone_number)
async def register_get_address_house(message: types.Message, state: FSMContext):
    await state.set_state(RegisterState.address_house)
    if not message.text.isnumeric():
        await message.reply(text="Введите корректный номер дома")
        return

    house_num = int(html.quote(message.text))
    if house_num > 49 or house_num < 42:
        await message.reply(text="Введите корректный номер дома")
        return
    await state.update_data(user_address_house=house_num)
    await message.answer(f"Ввведите номер вашей квартиры: (Только цифрами)", reply_markup=types.ReplyKeyboardRemove())


@router.message(RegisterState.address_house)
async def register_get_address_apartment(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.set_state(RegisterState.address_apartment)
    if not message.text.isnumeric():
        await message.reply(text="Введите корректный номер квартиры")
        return

    apartment_num = int(html.quote(message.text))
    if apartment_num > 90 or apartment_num < 0:
        await message.reply(text="Введите корректный номер квартиры")
        return
    await state.update_data(user_address_apartment=apartment_num)
    user_data = await state.get_data()

    sql_get_address_id = select(Address).where(Address.house == int(user_data['user_address_house']),
                                               Address.apartment == int(user_data['user_address_apartment']))

    address_res = await session.execute(sql_get_address_id)
    address: List[Address] = address_res.first()
    if not address:
        await message.reply(text="Адрес не существует в базе")
        return

    await message.answer(f"Ваша заявка была принята:", reply_markup=types.ReplyKeyboardRemove())
    text = f"Ник: {message.from_user.full_name}\n"
    text += f"Имя: {user_data['fio']}\n"
    text += f"Телефон: {user_data['user_phone']}\n"
    text += f"Дом: {user_data['user_address_house']}\n"
    text += f"Квартира: {user_data['user_address_apartment']}"
    await message.answer(text=text)
    await message.answer(f"Домком может Вам позвонить по номеру {user_data['user_phone']} для уточнения деталей")
    await message.answer(f"Если Ваш телеграм номер недоступна для входящих звонков, могут быть задержки одобрения")

    current_user = await db.select_current_user(message=message, session=session)
    sql_phone = insert(Phone).values(numbers=user_data['user_phone'],
                                     user_id=current_user.id)
    sql_propiska = insert(Propiska).values(user_id=current_user.id,
                                           address_id=address[0].id)
    sql_user = update(User).values(fio=user_data['fio']).where(User.telegram_id == message.from_user.id)

    await session.execute(sql_phone)
    await session.execute(sql_propiska)
    await session.execute(sql_user)
    await session.commit()

    await state.clear()
