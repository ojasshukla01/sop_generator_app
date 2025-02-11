from fastapi import FastAPI, Depends, HTTPException, status, Query, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from pydantic import BaseModel
from database import SessionLocal, engine, Base
import models
import logging
from schemas import SOPRequest
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pytz
from models import SOPRecord
from openai import OpenAI # Add this to your FastAPI project
from fpdf import FPDF  # For PDF generation
from docx import Document  # For DOCX generation
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import openai

# Load the .env file
load_dotenv()

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, generate a sample SOP"}]
)
print(response['choices'][0]['message']['content'])

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth2 and password hashing configuration
SECRET_KEY = "a_very_secret_key"  # Replace with a secure key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions for authentication
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(pytz.UTC) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(models.User).filter(models.User.username == username).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Pydantic models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    plain_password: str
    hashed_password: str
    class Config:
        orm_mode = True

class AcademicInfo(BaseModel):
    degree: str
    university: str
    year: str
    gpa: str

class Experience(BaseModel):
    role: str
    company: str
    duration: str
    description: str

class SOPRequest(BaseModel):
    fullName: str
    purposeStatement: str
    academicInfo: List[AcademicInfo]
    experience: List[Experience]

# Authentication endpoint (Login)
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for username: {form_data.username}")
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    if not user:
        logger.error(f"User not found for username: {form_data.username}")
        raise HTTPException(status_code=401, detail="User not found")
    
    logger.info(f"Comparing plain_password {user.plain_password} with {form_data.password}")
    if user.plain_password != form_data.password:
        logger.error(f"Password mismatch for username: {form_data.username}")
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"Login successful for username: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}


# User registration endpoint
@app.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(
        username=user.username,
        email=user.email,
        plain_password=user.password,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Get current user info
@app.get("/users/me", response_model=UserResponse)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    logger.info(f"Token received: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        logger.info(f"Decoded username: {username}")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(models.User).filter(models.User.username == username).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError as e:
        logger.error(f"Token decoding error: {e}")
        raise HTTPException(status_code=401, detail="Token is either expired or invalid.")


# CRUD operations for user management with pagination and filtering
@app.get("/users/", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100, description="Number of users to retrieve"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    username: str | None = None,
    email: str | None = None
):
    query = db.query(models.User)
    if username:
        query = query.filter(models.User.username.ilike(f"%{username}%"))
    if email:
        query = query.filter(models.User.email.ilike(f"%{email}%"))
    users = query.offset(offset).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user.username
    db_user.email = user.email
    db_user.hashed_password = hash_password(user.password)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

# SOP generation endpoint
def generate_sop_with_chatgpt(request: SOPRequest):
    prompt = f"""
    Write a personalized SOP for a student applying for a {request.purposeStatement} program at an international university. 
    Here is the student information:
    - Full Name: {request.fullName}
    - Academic Information: {', '.join([f"{info.degree} from {info.university} in {info.year} with GPA {info.gpa}" for info in request.academicInfo])}
    - Work Experience: {', '.join([f"{exp.role} at {exp.company} for {exp.duration}" for exp in request.experience])}
    
    Keep the tone professional and warm. The SOP should be 700-1000 words long.
    """

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant for generating SOPs."},
        {"role": "user", "content": "Write a detailed SOP for the following student application."}
    ],
    max_tokens=1000,
    temperature=0.7
)
    generated_text = response['choices'][0]['message']['content']
    return generated_text



@app.post("/generate_sop")
async def generate_sop(request: SOPRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        # Generate SOP content using ChatGPT
        sop_content = generate_sop_with_chatgpt(request)

        # Create SOPRecord
        sop_record = models.SOPRecord(
            full_name=request.fullName,
            purpose_statement=request.purposeStatement,
            sop_content=sop_content,
            user_id=current_user.id
        )
        db.add(sop_record)
        db.flush()  # This will populate sop_record.id with the new record's ID

        # Add academic info
        for info in request.academicInfo:
            academic = models.AcademicInfo(
                degree=info.degree,
                university=info.university,
                year=info.year,
                gpa=info.gpa,
                sop_record_id=sop_record.id  # Associate with the newly created SOPRecord
            )
            db.add(academic)

        # Add experience
        for exp in request.experience:
            experience = models.Experience(
                role=exp.role,
                company=exp.company,
                duration=exp.duration,
                description=exp.description,
                sop_record_id=sop_record.id  # Associate with the newly created SOPRecord
            )
            db.add(experience)

        # Commit all changes
        db.commit()
        logging.info(f"SOP saved with academic info and experience for user: {current_user.username}")

        return {"message": "SOP generated successfully!", "sop_content": sop_content}
    
    except Exception as e:
        db.rollback()  # Rollback in case of any error
        logging.error(f"Error generating SOP: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate SOP.")

    

@app.post("/download_sop")
async def download_sop(sop_content: str = Body(...), format: str = "pdf"):
    try:
        filename = f"sop.{format}"
        if format == "pdf":
            save_as_pdf(sop_content, filename)
        elif format == "docx":
            save_as_docx(sop_content, filename)
        elif format == "txt":
            save_as_txt(sop_content, filename)
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
        
        return FileResponse(filename, media_type="application/octet-stream", filename=filename)
    except Exception as e:
        logging.error(f"Error generating file: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate the file.")
    finally:
        if os.path.exists(filename):
            os.remove(filename)  # Clean up the temporary file

    

# Generate PDF
def save_as_pdf(sop_content, filename="sop.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, sop_content)
    pdf.output(filename)
    return filename

# Generate DOCX
def save_as_docx(sop_content, filename="sop.docx"):
    doc = Document()
    doc.add_paragraph(sop_content)
    doc.save(filename)
    return filename

# Generate TXT
def save_as_txt(sop_content, filename="sop.txt"):
    with open(filename, "w") as txt_file:
        txt_file.write(sop_content)
    return filename


@app.get("/")
def read_root():
    return {"message": "Welcome to the SOP Generator API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)




