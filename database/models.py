from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, UTC
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="student")
    
Base = declarative_base()

class SOP(Base):
    __tablename__ = "sops"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    sop_content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
