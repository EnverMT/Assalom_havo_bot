from typing import List

from aiogram import types, Dispatcher
from aiogram.utils.markdown import quote_html
from aiogram.dispatcher import FSMContext
from sqlalchemy import insert, select, update

from tgbot.keyboards.reply import contact_request
from tgbot.misc.states import RegisterState
from tgbot.models.models import Phone, Address, Propiska, User
from tgbot.services.DbCommands import DbCommands

"""
[ ] To do validation of all inputs in all methods
[x] To use memoryStorage, and save data to Database at final step only
"""

db = DbCommands()


async def check_register_status(message: types.Message, state: FSMContext):
    user = await db.select_current_user(message=message)

    if not user:
        return

    if user.isApproved:
        await message.answer(text=f"Вы уже прошли регистрацию {user.full_name}")
        return

    phones = await user.get_phones(message)
    if phones:
        await message.answer(text="Ваша заявка под рассмотрением")
        return

    await message.answer(text=f"Для продолжения регистрации, прошу написать Фамилию и Имю {user.full_name}")
    await RegisterState.ReadyToRegister.set()


async def register_get_fio(message: types.Message, state: FSMContext):
    await RegisterState.fio.set()
    await state.update_data(fio=quote_html(message.text))

    await message.answer(text=f"Прошу предоставит ваш телефон Контакт.",
                         reply_markup=contact_request)


async def register_get_contact(message: types.Message, state: FSMContext):
    await RegisterState.phone_number.set()
    await state.update_data(user_phone=message.contact.phone_number)

    await message.answer(f"Ввведите номер вашего дома: (Только цифрами)", reply_markup=types.ReplyKeyboardRemove())
    await RegisterState.address_house.set()

async def register_get_address_house(message: types.Message, state: FSMContext):
    if not message.text.isnumeric():
        await message.reply(text="Введите корректный номер дома")
        return

    house_num = int(quote_html(message.text))
    if house_num > 49 or house_num < 42:
        await message.reply(text="Введите корректный номер дома")
        return
    await state.update_data(user_address_house=house_num)

    await RegisterState.address_apartment.set()
    await message.answer(f"Ввведите номер вашей квартиры: (Только цифрами)", reply_markup=types.ReplyKeyboardRemove())


async def register_get_address_apartment(message: types.Message, state: FSMContext):

    if not message.text.isnumeric():
        await message.reply(text="Введите корректный номер квартиры")
        return

    apartment_num = int(quote_html(message.text))
    if apartment_num > 90 or apartment_num < 0:
        await message.reply(text="Введите корректный номер квартиры")
        return
    await state.update_data(user_address_apartment=apartment_num)
    user_data = await state.get_data()

    sql_get_address_id = select(Address).where(Address.house == int(user_data['user_address_house']),
                                               Address.apartment == int(user_data['user_address_apartment']))
    db_session = message.bot.get("db")
    async with db_session() as session:
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

    current_user = await db.select_current_user(message=message)
    sql_phone = insert(Phone).values(numbers=user_data['user_phone'],
                                     user_id=current_user.id)
    sql_propiska = insert(Propiska).values(user_id=current_user.id,
                                           address_id=address[0].id)
    sql_user = update(User).values(fio=user_data['fio']).where(User.telegram_id == message.from_user.id)

    async with db_session() as session:
        await session.execute(sql_phone)
        await session.execute(sql_propiska)
        await session.execute(sql_user)
        await session.commit()

    await state.finish()
    await state.reset_state()


def register_register_menu(dp: Dispatcher):
    dp.register_message_handler(check_register_status, commands=["register"], state='*')
    dp.register_message_handler(register_get_fio, state=RegisterState.ReadyToRegister)
    dp.register_message_handler(register_get_contact,
                                state=RegisterState.fio,
                                content_types=types.ContentType.CONTACT)
    dp.register_message_handler(register_get_address_house,
                                state=RegisterState.address_house)
    dp.register_message_handler(register_get_address_apartment,
                                state=RegisterState.address_apartment)