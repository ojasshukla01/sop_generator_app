from fastapi import APIRouter, Depends
from auth.auth import create_access_token, hash_password, verify_password
from database import get_user_by_username, create_user

router = APIRouter()

@router.post("/register")
def register(username: str, password: str):
    hashed_password = hash_password(password)
    create_user(username, hashed_password)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(username: str, password: str):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        return {"error": "Invalid username or password"}
    
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}
