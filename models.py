from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    plain_password = Column(String)  # This needs to be in your model

def upgrade():
    # Add the column with a default value for existing rows
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    
    # Fill in a default value for all existing rows (e.g., 'default_username')
    op.execute("UPDATE users SET username = 'default_username' WHERE username IS NULL")
    
    # Alter the column to be NOT NULL after backfilling
    op.alter_column('users', 'username', nullable=False)
