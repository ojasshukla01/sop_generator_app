from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "postgresql+psycopg2://sop_app_user:R3yIrYmWSruauVUPL9Hghysi4ZVD6gba@dpg-cuk0ec5ds78s739jqqug-a.oregon-postgres.render.com:5432/sop_app"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(metadata=MetaData())

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    # Optional: Test the connection or perform sample data insertion
    with engine.connect() as connection:
        print("Database connection successful!")
