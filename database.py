from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


load_dotenv()
DATABASE_URL = str(os.getenv("DATABASE_URL"))

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db
