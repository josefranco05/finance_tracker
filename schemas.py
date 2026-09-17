from pydantic import BaseModel, Field, ConfigDict, EmailStr

class TransactionBase(BaseModel):
    transaction_type: str = Field(min_length=1, max_length=10)
    value: float
    date: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: int
    user_id: int
    category_id: int
    created_at: str
    updated_at: str

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
    create_date: str
    deleted_at: str