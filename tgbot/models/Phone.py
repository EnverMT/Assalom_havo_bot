from sqlalchemy import Column, String, DateTime, ForeignKey, \
    Integer
from sqlalchemy.sql import func

from tgbot.services.Base import Base


class Phone(Base):
    __tablename__ = 'phones'

    id = Column(Integer, primary_key=True)
    numbers = Column(String(15), unique=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return "<Phone(id='{}', numbers='{}', user_id='{}')>".format(
            self.id, self.numbers, self.user_id)