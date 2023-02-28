from aiogram.dispatcher.filters.state import StatesGroup, State

class RegisterState(StatesGroup):
    ReadyToRegister = State()
    phone_number = State()
    address_house = State()
    address_apartment = State()
    FinalStep = State()


class AdminState(StatesGroup):
    Menu = State()
    ListOfWaitingApprovalUsers = State()
    WaitingApproval = State()


class UserState(StatesGroup):
    Menu = State()
    InfoAboutMe = State()

class UserDataState(StatesGroup):
    test_data = State()