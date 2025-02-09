from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from pydantic import BaseModel
from database import SessionLocal, engine
import models
import logging
from schemas import SOPRequest
from fastapi.middleware.cors import CORSMiddleware

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to a specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OAuth2 configuration
SECRET_KEY = "a_very_secret_key"  # Replace with a secure key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic schemas for user management
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(models.User).filter(models.User.name == username).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Authentication endpoint (Login)
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.name == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.name}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# User Registration
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Get Current User Info
@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    return current_user

# CRUD Endpoints for User Management (with Pagination and Filtering)
@app.get("/users/", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    name: str | None = None,
    email: str | None = None
):
    query = db.query(models.User)
    if name:
        query = query.filter(models.User.name.ilike(f"%{name}%"))
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
def update_user(user_id: int, user: UserBase, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.email = user.email
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

# SOP Generation Endpoint
@app.post("/generate_sop")
async def generate_sop(request: SOPRequest, db: Session = Depends(get_db)):
    """
    Endpoint to generate an SOP based on user input.
    """
    logger.info(f"Received SOP request for: {request.full_name}")
    
    sop_content = f"""
    Dear Admissions Committee,

    My name is {request.full_name}, and I am interested in applying to your program...

    Purpose: {request.purpose_statement}

    Academic History:
    """
    for academic in request.academic_info:
        sop_content += f"- {academic.degree} from {academic.university} ({academic.year}), GPA: {academic.gpa}\n"
    
    sop_content += "\nProfessional Experience:\n"
    for exp in request.experience:
        sop_content += f"- {exp.role} at {exp.company} for {exp.duration}.\n  Description: {exp.description}\n"
    
    logger.info("Generated SOP content:\n" + sop_content)
    
    return {"message": "SOP generated successfully!", "sop_content": sop_content}
