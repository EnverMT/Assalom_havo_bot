from aiogram.dispatcher.filters.state import StatesGroup, State

class RegisterState(StatesGroup):
    ReadyToRegister = State()
    phone_number = State()
    fio = State()
    house = State()
    apartment = State()
    final = State()

class AdminRegisterState(StatesGroup):
    AwaitingUsersList = State()
    ApprovalUsers = State()