from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy import insert

from tgbot.keyboards.reply import contact_request
from tgbot.misc.states import RegisterState
from tgbot.models.models import Phone, Address
from tgbot.services.DbCommands import DbCommands

"""
[ ] To do validation of all inputs in all methods
[ ] To use memoryStorage, and save data to Database at final step only
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

    await message.answer(text=f"Для продолжения регистрации, прошу предоставит ваши Контакты {user.full_name}", reply_markup=contact_request)
    await RegisterState.ReadyToRegister.set()


async def register_get_contact(message: types.Message, state: FSMContext):
    await RegisterState.phone_number.set()
    await state.update_data(user_phone=message.contact.phone_number)
    await message.answer(f"Ввведите номер вашего дома: ", reply_markup=types.ReplyKeyboardRemove())
    await RegisterState.address_house.set()


async def register_get_address_house(message: types.Message, state: FSMContext):
    if not message.text.isnumeric():
        await message.reply(text="Введите корректный номер дома")
        return

    house_num = int(message.text)
    if house_num > 49 or house_num < 42:
        await message.reply(text="Введите корректный номер дома")
        return
    await state.update_data(user_address_house=house_num)

    await RegisterState.address_apartment.set()
    await message.answer(f"Ввведите номер вашей квартиры: ", reply_markup=types.ReplyKeyboardRemove())


async def register_get_address_apartment(message: types.Message, state: FSMContext):
    if not message.text.isnumeric():
        await message.reply(text="Введите корректный номер квартиры")
        return

    apartment_num = int(message.text)
    if apartment_num > 90 or apartment_num < 0:
        await message.reply(text="Введите корректный номер квартиры")
        return
    await state.update_data(user_address_apartment=apartment_num)

    await message.answer(f"Ваша заявка была принята:", reply_markup=types.ReplyKeyboardRemove())
    user_data = await state.get_data()
    text = f"Имя: {message.from_user.full_name}\n"
    text += f"Телефон: {user_data['user_phone']}\n"
    text += f"Дом: {user_data['user_address_house']}\n"
    text += f"Квартира: {user_data['user_address_apartment']}"
    await message.answer(text=text)
    current_user = await db.select_current_user(message=message)

    sql_phone = insert(Phone).values(numbers=user_data['user_phone'],
                                     user_id=current_user.id)
    sql_address = insert(Address).values(house=int(user_data['user_address_house']),
                                         apartment=int(user_data['user_address_apartment']),
                                         user_id=current_user.id)

    db_session = message.bot.get("db")
    async with db_session() as session:
        await session.execute(sql_phone)
        await session.execute(sql_address)
        await session.commit()

    await state.finish()
    await state.reset_state()


def register_register_menu(dp: Dispatcher):
    dp.register_message_handler(check_register_status, commands=["register"], state='*')
    dp.register_message_handler(register_get_contact,
                                state=RegisterState.ReadyToRegister,
                                content_types=types.ContentType.CONTACT)
    dp.register_message_handler(register_get_address_house,
                                state=RegisterState.address_house)
    dp.register_message_handler(register_get_address_apartment,
                                state=RegisterState.address_apartment)