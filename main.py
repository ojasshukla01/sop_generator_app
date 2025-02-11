from fastapi import FastAPI, Depends, HTTPException, status, Query, Body
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
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
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
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    return current_user

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
@app.post("/generate_sop")
async def generate_sop(request: SOPRequest, db: Session = Depends(get_db)):
    logger.info(f"Generating SOP for: {request.fullName}")
    # Process the request and return a response
    return {"message": "SOP generated successfully!", "sop_content": "Generated SOP content here"}

