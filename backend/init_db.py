"""
Initialize database with permissions
Run this script after creating the database
"""
from app.core.database import SessionLocal
from app.utils.init_permissions import init_permissions

if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Initializing database...")
        init_permissions(db)
        print("Database initialized successfully!")
    finally:
        db.close()
