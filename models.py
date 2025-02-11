from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import pytz

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    plain_password = Column(String)  # This needs to be in your model

class AcademicInfo(Base):
    __tablename__ = "academic_info"
    
    id = Column(Integer, primary_key=True, index=True)
    degree = Column(String, nullable=False)
    university = Column(String, nullable=False)
    year = Column(String, nullable=False)
    gpa = Column(String, nullable=False)
    sop_record_id = Column(Integer, ForeignKey("sop_records.id"), nullable=False)

class Experience(Base):
    __tablename__ = "experience"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    company = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    sop_record_id = Column(Integer, ForeignKey("sop_records.id"), nullable=False)

class SOPRecord(Base):
    __tablename__ = "sop_records"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    purpose_statement = Column(Text, nullable=False)
    sop_content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    
    user = relationship("User", backref="sop_records")
    academic_info = relationship("AcademicInfo", backref="sop_record", cascade="all, delete-orphan")
    experience = relationship("Experience", backref="sop_record", cascade="all, delete-orphan")
