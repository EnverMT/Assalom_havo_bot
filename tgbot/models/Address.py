from sqlalchemy import Column, String, Integer

from tgbot.services.Base import Base


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    house = Column(Integer, nullable=False)
    apartment = Column(Integer, nullable=False)
    gaz_litsevoy_schet = Column(Integer)
    owner_fio = Column(String(100))
    owner_tel = Column(String(20))
    room_size = Column(String(20))
    kadastr_number = Column(String(30))
    gaz_schetchik_nomer = Column(String(20))
    musor_ls = Column(String(30))

    def __repr__(self):
        return "<Address(id='{}', house='{}', apartment='{}')>".format(
            self.id, self.house, self.apartment)