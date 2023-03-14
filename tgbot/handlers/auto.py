from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.inline import AutoMenu
from tgbot.services.DbCommands import DbCommands
import tgbot.misc.states as states

db = DbCommands()


async def auto_info_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await states.AutoInfoState.Menu.set()




    await call.bot.send_message(chat_id=call.from_user.id, text="Автомобиль", reply_markup=AutoMenu)


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
    pass


def register_auto(dp: Dispatcher):
    dp.register_callback_query_handler(auto_info_menu, state='*', text="auto_info_menu")
    dp.register_callback_query_handler(auto_list_my_cars, state=states.AutoInfoState.Menu, text="auto_list_my_cars")
    dp.register_callback_query_handler(auto_find_owner_by_number, state=states.AutoInfoState.Menu, text="auto_find_owner_by_number")
    dp.register_message_handler(auto_find_owner_by_number_result, state=states.AutoInfoState.auto_find_owner_by_number)