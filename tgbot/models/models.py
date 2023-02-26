from sqlalchemy import (Column, Integer, BigInteger, String,
                        Sequence, TIMESTAMP, Boolean, JSON)
from sqlalchemy import sql
from tgbot.services.db import db

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger)
    full_name = Column(String(100))
    fio = Column(String(100))
    username = Column(String(50))
    phone_number = Column(String(15))
    house_number = Column(Integer)
    apartment_number = Column(Integer)
    awaiting_register = Column(Boolean)
    isRegistered = Column(Boolean)
    canRegisterUser = Column(Boolean)
    whoRegistered = Column(Integer)
    query: sql.Select

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)