from database import Base, engine
from models.models import User, Categories, Transactions
from datetime import datetime
from sqlalchemy.orm import Session
from typing_extensions import List
import math
import pandas as pd

with Session(engine) as session:
    # Insert a new user
    new_user = User(
        user_id=3,
        first_name="Evelin Valentina",
        last_name="Bedoya",
        username="valenbe",
        email="example3@example.com",
        password_hash="hashed_password",
        create_date=datetime.now(),
        deleted_at=None
    )

    session.add(new_user)
    session.commit()
    session.close()
