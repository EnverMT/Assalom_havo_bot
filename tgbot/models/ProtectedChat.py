from sqlalchemy import Column, BigInteger, Integer

from tgbot.services.Base import Base


class ProtectedChat(Base):
    __tablename__ = 'protected_chats'

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, nullable=True)
    thread_id = Column(BigInteger, nullable=True)

    def __repr__(self):
        return "<ProtectedChat(id='{}', chat_id='{}', thread_id='{}')>".format(
            self.id, self.chat_id, self.thread_id)