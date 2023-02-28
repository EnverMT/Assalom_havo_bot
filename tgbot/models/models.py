from sqlalchemy import Column, Integer, BigInteger, String, Boolean, TIMESTAMP
from sqlalchemy import sql
from sqlalchemy import ForeignKey
from sqlalchemy import Integer


from tgbot.services.Base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    full_name = Column(String(100))
    username = Column(String(50))
    isApproved = Column(Boolean)
    whoApproved = Column(BigInteger)

    query: sql.Select

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)


class Phone(Base):
    __tablename__ = 'phones'

    id = Column(Integer, primary_key=True)
    numbers = Column(String(15), unique=True)
    user_id = Column(BigInteger, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True))

    def __repr__(self):
        return "<Phone(id='{}', numbers='{}', user_id='{}')>".format(
            self.id, self.numbers, self.user_id)