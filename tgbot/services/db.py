from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from load_all import config

SQL_URL = f"postgresql://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.database}"

engine = create_engine(SQL_URL)

Session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = Session_local()
    try:
        yield db
    finally:
        db.close()