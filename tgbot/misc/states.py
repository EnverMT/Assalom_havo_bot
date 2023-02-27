from aiogram.dispatcher.filters.state import StatesGroup, State

class RegisterState(StatesGroup):
    ReadyToRegister = State()
    phone_number = State()


class AdminState(StatesGroup):
    Menu = State()
    ListOfWaitingApprovalUsers = State()


class UserState(StatesGroup):
    Menu = State()
    InfoAboutMe = State()