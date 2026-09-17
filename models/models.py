from __future__ import annotations
from sqlalchemy import String, ForeignKey, Integer, Text, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from datetime import date, datetime, UTC


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    create_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=lambda: datetime.now(UTC))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    transactions: Mapped[list[Transactions]] = relationship(back_populates="user_id_transactions")
    categories: Mapped[list[Categories]] = relationship(back_populates="user_id_categories")

class Categories(Base):
    __tablename__ = "categories"

    category_id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    obsolete: Mapped[bool] = mapped_column(nullable=False, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=True, index=True)

    user_id_categories: Mapped[User] = relationship(back_populates="categories")

class Transactions(Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"), nullable=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    transaction_type: Mapped[str] = mapped_column(String(255), nullable=False)
    valor: Mapped[float] = mapped_column(nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=lambda: datetime.now(UTC))

    user_id_transactions: Mapped[User] = relationship(back_populates="transactions")