from sqlalchemy import Column, DateTime, UniqueConstraint, ForeignKey, Integer
from sqlalchemy.sql import func

from tgbot.services.Base import Base


class Propiska(Base):
    __tablename__ = 'propiska'
    __table_args__ = (UniqueConstraint('user_id', 'address_id'),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    address_id = Column(Integer, ForeignKey("address.id", onupdate="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return "<Propiska(id='{}', user_id='{}', address_id='{}')>".format(
            self.id, self.user_id, self.address_id)