"""
Seed script to create initial owner account.
Run this after database migrations: python seed_owner.py
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
load_dotenv()

from database import SessionLocal
from models.user import User, UserRole
from utils.security import get_password_hash


def create_owner():
    """Create initial owner account."""
    db: Session = SessionLocal()
    
    try:
        # Check if owner already exists
        existing_owner = db.query(User).filter(
            User.role == UserRole.OWNER
        ).first()
        
        if existing_owner:
            print(f"⚠️  Owner account already exists: {existing_owner.email}")
            return
        
        # Create owner account with a simple password
        password = "admin123"
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
            
        owner = User(
            email="owner@lemihotel.com",  # Change this to your email
            password_hash=get_password_hash(password),
            full_name="Hotel Owner",
            phone="+251912345678",  # Change to your phone
            role=UserRole.OWNER,
            is_active=True
        )
        
        db.add(owner)
        db.commit()
        db.refresh(owner)
        
        print(f"✅ Owner account created successfully!")
        print(f"   Email: {owner.email}")
        print(f"   Password: admin123")
        print(f"   ⚠️  IMPORTANT: Change this password immediately after first login!")
        
    except Exception as e:
        print(f"❌ Error creating owner account: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding initial owner account...")
    create_owner()
