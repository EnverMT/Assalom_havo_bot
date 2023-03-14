from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.inline import AutoMenu
from tgbot.services.DbCommands import DbCommands
import tgbot.misc.states as states

db = DbCommands()


async def auto_info_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await states.AutoInfoState.Menu.set()

    user = await db.select_current_user(call)
    autos = await user.get_autos(call=call)

    await call.bot.send_message(chat_id=call.from_user.id, text="Autos", reply_markup=AutoMenu)



def register_auto(dp: Dispatcher):
    dp.register_callback_query_handler(auto_info_menu, state='*', text="auto_info_menu")