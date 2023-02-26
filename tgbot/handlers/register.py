from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from tgbot.keyboards.inline import RegisterFinish

from tgbot.misc.states import RegisterState

import tgbot.services.database

database = tgbot.services.database.DBCommands()


async def check_register_status(message: types.Message, state : FSMContext):
    user = await database.get_user(message.from_user.id)

    if not user:
        await register(message=message)
        return

    if user.isRegistered:
        await message.answer("Вы уже зарегистрированы")
        return

    if user.awaiting_register:
        await message.answer("Ваша заявка под рассмотрением")
        return

    await register(message=message)

async def register(message: types.Message):
    from tgbot.keyboards.reply import contact_request
    user = await database.add_new_user()
    await message.answer(f"Здравствуйте, для продолжения прошу предоставить ваши контактные данные {user.username}",
                         reply_markup=contact_request)
    await RegisterState.ReadyToRegister.set()

async def register_get_contact_callback(message: types.Message):
    await database.register_add_phone_number(message.contact.phone_number)
    await message.answer(f"Введите Ваше Ф.И.О.",reply_markup=types.ReplyKeyboardRemove())
    await RegisterState.phone_number.set()

async def register_get_fio(message: types.Message):
    await database.register_add_fio(message.text)
    await message.answer(f"Введите ваш номер дома:")
    await RegisterState.fio.set()

async def register_get_house_number(message: types.Message):
    await database.register_add_house_number(int(message.text))
    await message.answer(f"Введите ваш номер квартиры:")
    await RegisterState.house.set()

async def register_get_apartment_number(message: types.Message):
    await database.register_add_apartment_number(int(message.text))
    user = await database.get_user(message.from_user.id)
    summary = f"Суммарная информация:\nФИО: {user.fio}\nТелефон: {user.phone_number}\nАдрес: {user.house_number} / {user.apartment_number}"
    await message.answer(text=summary)
    await message.answer("Проверьте правильность данных перед отправкой", reply_markup=RegisterFinish)
    await RegisterState.apartment.set()

async def register_final_callback(message: types.CallbackQuery, state : FSMContext):
    if message.data == "register_finish":
        await RegisterState.final.set()
        await database.register_final()
        await message.message.edit_reply_markup()
        await message.answer("Ваша заявка принята к рассмотрению")


def register_register_menu(dp: Dispatcher):
    dp.register_message_handler(check_register_status, commands=["register"], state='*')
    dp.register_message_handler(register_get_contact_callback,
                                state=RegisterState.ReadyToRegister,
                                content_types=types.ContentType.CONTACT)
    dp.register_message_handler(register_get_fio, state=RegisterState.phone_number)
    dp.register_message_handler(register_get_house_number, state=RegisterState.fio)
    dp.register_message_handler(register_get_apartment_number, state=RegisterState.house)
    dp.register_callback_query_handler(register_final_callback, state=RegisterState.apartment)