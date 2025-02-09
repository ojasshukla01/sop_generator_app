from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class AcademicInfo(BaseModel):
    degree: str
    university: str
    year: str
    gpa: str

class Experience(BaseModel):
    company: str
    role: str
    duration: str
    description: str

class SOPRequest(BaseModel):
    full_name: str
    email: EmailStr
    dob: date
    contact_number: str
    academic_info: List[AcademicInfo]
    experience: List[Experience]
    purpose_statement: str
