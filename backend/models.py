from __future__ import annotations

from sqlalchemy import TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), default="admin")
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, index=True)
    username = Column(String(100))
    fullname = Column(String(100))
