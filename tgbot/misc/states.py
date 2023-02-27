from aiogram.dispatcher.filters.state import StatesGroup, State

class RegisterState(StatesGroup):
    ReadyToRegister = State()
    phone_number = State()


class AdminRegisterState(StatesGroup):
    AwaitingUsersList = State()
    ApprovalUsers = State()


class UserState(StatesGroup):
    Menu = State()
    InfoAboutMe = State()