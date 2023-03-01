from aiogram.dispatcher.filters.state import StatesGroup, State


class RegisterState(StatesGroup):
    ReadyToRegister = State()
    fio = State()
    phone_number = State()
    address_house = State()
    address_apartment = State()
    FinalStep = State()


class UserApprovalState(StatesGroup):
    ListOfWaitingApprovalUsers = State()
    WaitingApprovalUser = State()


class AdminState(StatesGroup):
    Menu = State()


class DomkomControlState(StatesGroup):
    ListOfDomkoms = State()
    AddNewDomkom = State()
    AssignNewDomkom = State()


class DomkomState(StatesGroup):
    Menu = State()


class UserState(StatesGroup):
    Menu = State()
    InfoAboutMe = State()