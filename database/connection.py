from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://sop_app_user:R3yIrYmWSruauVUPL9Hghysi4ZVD6gba@dpg-cuk0ec5ds78s739jqqug-a.oregon-postgres.render.com/sop_app"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Ensure tables are created
Base.metadata.create_all(bind=engine)
