from aiogram import Router, F, types, enums
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot import bot
from tgbot.services.DbCommands import DbCommands

db = DbCommands()

router = Router()


@router.callback_query(F.data == "info_aboutme", F.message.chat.type == enums.ChatType.PRIVATE)
async def info_about_me(call: types.CallbackQuery, session: AsyncSession):
    await call.message.edit_reply_markup()

    user = await db.select_current_user(call, session=session)
    text = f"Ник: {user.full_name}\n"
    text += f"Имя: {user.fio}\n\n"

    addr = await user.get_addresses(session=session)

    phones = await user.get_phones(session=session)
    for p in phones:
        text += f"Tel: {p.numbers}\n"
    await bot.send_message(chat_id=call.from_user.id, text=f"{text}")

    for a in addr:
        text = f"\nAddress: {a.house}/{a.apartment}\n"
        text += f"Размер квартиры - {a.room_size}\n"
        text += f"Номер кадастра - <code>{a.kadastr_number}</code>\n"

        text += f"\nГаз л.с. - <code>{a.gaz_litsevoy_schet}</code>\n"
        text += f"Номер счетчика газа - {a.gaz_schetchik_nomer}\n"

        text += f"\nМусор л.с. - <code>{a.musor_ls}</code>\n"
        await bot.send_message(chat_id=call.from_user.id, text=f"{text}")


@router.message(Command('cancel'), F.message.chat.type == enums.ChatType.PRIVATE)
async def cancel(message: types.Message, state: FSMContext):
    """
      Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())