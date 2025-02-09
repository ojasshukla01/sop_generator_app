import os
from dotenv import load_dotenv

load_dotenv()
 # Load environment variables from .env file (if available)

SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASE_URL = os.environ.get("postgresql://sop_app_user:R3yIrYmWSruauVUPL9Hghysi4ZVD6gba@dpg-cuk0ec5ds78s739jqqug-a/sop_app")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
