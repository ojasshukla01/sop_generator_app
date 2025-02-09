# crud.py
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserUpdate

# Retrieve all users
def get_all_users(db: Session):
    return db.query(User).all()

# Retrieve a user by ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Create a new user
def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Update an existing user
def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.name = user.name
        db_user.email = user.email
        db.commit()
        db.refresh(db_user)
    return db_user

# Delete a user
def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
