from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.services.DbCommands import DbCommands

db = DbCommands()


async def info_about_me(call: types.CallbackQuery):
    await call.message.edit_reply_markup()

    user = await db.select_current_user(call)
    text = f"Ник: {user.full_name}\n"
    text += f"Имя: {user.fio}\n\n"

    addr = await user.get_addresses(call=call)

    phones = await user.get_phones(call=call)
    for p in phones:
        text += f"Tel: {p.numbers}\n"
    await call.bot.send_message(chat_id=call.from_user.id, text=f"{text}")

    for a in addr:
        text = f"\nAddress: {a.house}/{a.apartment}\n"
        text += f"Размер квартиры - {a.room_size}\n"
        text += f"Номер кадастра - <code>{a.kadastr_number}</code>\n"

        text += f"\nГаз л.с. - <code>{a.gaz_litsevoy_schet}</code>\n"
        text += f"Номер счетчика газа - {a.gaz_schetchik_nomer}\n"

        text += f"\nМусор л.с. - <code>{a.musor_ls}</code>\n"
        await call.bot.send_message(chat_id=call.from_user.id, text=f"{text}")


async def cancel(message: types.Message, state: FSMContext):
    """
      Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


def register_common(dp: Dispatcher):
    dp.register_callback_query_handler(info_about_me, state='*', text_contains="info_aboutme",
                                       chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(cancel, state='*', commands=['cancel'], chat_type=types.ChatType.PRIVATE)