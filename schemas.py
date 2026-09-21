from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UserBase(BaseModel):
    username: str = Field(min_length=5)
    email: EmailStr
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    create_date: datetime
    status: str


class TransactionBase(BaseModel):
    transaction_type: str = Field(min_length=1, max_length=10)
    category: str = Field(min_length=1, max_length=100)
    value: float
    date: datetime
    description: str | None = Field(max_length=140, default=None)

class TransactionCreate(TransactionBase):
    user_id: int # TEMPORAL

class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: int
    user_id: int
    created_at: datetime
