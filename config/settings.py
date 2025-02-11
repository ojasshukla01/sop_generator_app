import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()  # Move this to the top

# Define variables after loading .env
DATABASE_URL = os.environ.get("postgresql://sop_app_user:R3yIrYmWSruauVUPL9Hghysi4ZVD6gba@dpg-cuk0ec5ds78s739jqqug-a.oregon-postgres.render.com/sop_app")
SECRET_KEY = os.environ.get("SECRET_KEY")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create engine after DATABASE_URL is defined
engine = create_engine(DATABASE_URL)
