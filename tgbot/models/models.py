from sqlalchemy import (Column, Integer, BigInteger, String,
                        Sequence, TIMESTAMP, Boolean, JSON)
from sqlalchemy import sql
from tgbot.services.Base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    full_name = Column(String(100))
    fio = Column(String(100))
    username = Column(String(50))
    phone_number = Column(String(15))       # Что будет если у человека несколько телефонов?
    house_number = Column(Integer)          # Что будет если у человека несколько домов?
    apartment_number = Column(Integer)      # Что будет если у человека несколько квартир?
    awaiting_register = Column(Boolean)     # Изменить это на isAprroved
    isRegistered = Column(Boolean)          # Впринцпе можно отказатся от этой колонки
    canRegisterUser = Column(Boolean)       # Убрать эту колонку, сделать отдельную таблицу для домкомов и модераторов, и связать ForeignKey
    whoRegistered = Column(Integer)         # Изменить это на whoApproved
    query: sql.Select

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)