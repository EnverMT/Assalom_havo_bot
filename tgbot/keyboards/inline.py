from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

AdminMenu = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Добавить нового домкома", callback_data="add_new_domkom")],
            [InlineKeyboardButton(text="Список домкомов", callback_data="list_of_domkoms")],
            [InlineKeyboardButton(text="Список ожидаемых пользователей", callback_data="list_of_waiting_approval_users")]
        ]
    )

DomkomMenu = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Список ожидаемых пользователей", callback_data="list_of_waiting_approval_users")],
            [InlineKeyboardButton(text="Информация обо мне", callback_data="info_aboutme")]
        ]
    )


UserMenu = InlineKeyboardMarkup(
        inline_keyboard=
        [
       #     [InlineKeyboardButton(text="Найти владелца машины", callback_data="find_autos_owner")],
            [InlineKeyboardButton(text="Информация обо мне", callback_data="info_aboutme")]
        ]
    )

RegisterFinish = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Подтверждаю", callback_data="register_finish")]
        ]
    )