from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

AdminMenu = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Добавить нового домкома", callback_data="add_new_domkom")],
            [InlineKeyboardButton(text="Список домкомов", callback_data="list_of_domkoms")],
            [InlineKeyboardButton(text="Список зарегистрированных жителей", callback_data="list_of_approved_users")],
            [InlineKeyboardButton(text="Список ожидаемых пользователей", callback_data="list_of_waiting_approval_users")]
        ]
    )

DomkomMenu = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Список зарегистрированных жителей", callback_data="list_of_approved_users")],
            [InlineKeyboardButton(text="Список ожидаемых жителей", callback_data="list_of_waiting_approval_users")],
            [InlineKeyboardButton(text="Информация обо мне", callback_data="info_aboutme")]
        ]
    )

ListOfApprovedUsersMenu = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Фильтр по домам и квартирам", callback_data="list_of_approved_users_by_house")],
            [InlineKeyboardButton(text="Фильтр по номеру телефона", callback_data="list_of_approved_users_by_phone")],
            [InlineKeyboardButton(text="Фильтр по Имени", callback_data="list_of_approved_users_by_name")]
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