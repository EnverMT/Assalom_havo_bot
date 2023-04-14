from sqlalchemy import Column, String, DateTime, ForeignKey, \
    Integer
from sqlalchemy.sql import func

from tgbot.services.Base import Base


class Auto(Base):
    __tablename__ = 'auto'

    id = Column(Integer, primary_key=True)
    number = Column(String(15), unique=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return "<Auto(id='{}', number='{}', user_id='{}')>".format(
            self.id, self.number, self.user_id)