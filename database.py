"""Database models and CRUD operations using SQLAlchemy."""
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    """User model for authentication and credit management."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    credits = Column(Integer, default=5)

# Database setup
engine = create_engine('sqlite:///sculptor.db', echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def create_user(username: str, hashed_password: str) -> User:
    """Create a new user with 5 initial credits."""
    db = SessionLocal()
    try:
        user = User(username=username, hashed_password=hashed_password, credits=5)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

def get_user(username: str) -> User:
    """Get user by username."""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.username == username).first()
    finally:
        db.close()

def get_user_by_id(user_id: int) -> User:
    """Get user by ID."""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()

def update_credits(user_id: int, credits: int) -> bool:
    """Update user credits."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.credits = credits
            db.commit()
            return True
        return False
    finally:
        db.close()

def add_credits(user_id: int, amount: int) -> bool:
    """Add credits to user account."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.credits += amount
            db.commit()
            return True
        return False
    finally:
        db.close()

def deduct_credits(user_id: int, amount: int) -> bool:
    """Deduct credits from user account. Returns True if successful."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.credits >= amount:
            user.credits -= amount
            db.commit()
            return True
        return False
    finally:
        db.close()
