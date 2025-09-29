import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def create_db_engine():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    engine = create_engine(db_url)
    return engine

def test_connection():
    try:
        engine = create_db_engine()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT Version();"))
            row = result.fetchone()
            version_full = row[0] if row else "Unknown"
            version = version_full.split(" on ")[0]
            print(f"Database connection successful. PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
    
if __name__ == "__main__":
    test_connection()
    
