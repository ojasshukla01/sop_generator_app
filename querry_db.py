from sqlalchemy import create_engine, text

# Corrected connection URL
DATABASE_URL = "postgresql+psycopg2://sop_app_user:R3yIrYmWSruauVUPL9Hghysi4ZVD6gba@dpg-cuk0ec5ds78s739jqqug-a.oregon-postgres.render.com:5432/sop_app"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Execute a sample query
with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM users"))
    for row in result:
        print(dict(row))
