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
    AddNewDomkomFiltered = State()
    AssignNewDomkom = State()


class DomkomState(StatesGroup):
    Menu = State()


class UserListState(StatesGroup):
    Menu = State()
    FilterByHouse = State()
    FilterByPhone = State()
    FilterByName = State()


class UserState(StatesGroup):
    Menu = State()
    InfoAboutMe = State()


class AutoInfoState(StatesGroup):
    Menu = State()
    auto_find_owner_by_number = State()
    AutoAdd = State()
    AutoDelete = State()