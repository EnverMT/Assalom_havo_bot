from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func

from tgbot.services.Base import Base


class Domkom(Base):
    __tablename__ = 'domkoms'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    telegram_id = Column(BigInteger, nullable=False)
    whoAssigned = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return "<Domkom(id='{}', user_id='{}', whoAssigned='{}')>".format(
            self.id, self.user_id, self.whoAssigned)