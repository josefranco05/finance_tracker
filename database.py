from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# ---------------***--------------------***--------------
# SETUP FOR USE WITH PRODUCTION POSTGRESQL DATABASE
# load_dotenv()
# DATABASE_URL = str(os.getenv("DATABASE_URL"))

# engine = create_engine(DATABASE_URL)
# ---------------***--------------------***--------------

# ---------------***--------------------***--------------
# SETUP TO USE WITH LOCAL SQLITE DB FOR TESTING
engine = create_engine(
    "sqlite:///database.db",
    connect_args={"check_same_thread": False}
)
# # ---------------***--------------------***--------------

# INDEPENDENT
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 

class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as db:
        yield db


Base.metadata.create_all(bind=engine)