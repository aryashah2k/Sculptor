"""Authentication functions for user signup and login."""
import bcrypt
from database import create_user, get_user

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Convert password to bytes and hash it
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string for database storage
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # Convert both to bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    # Verify using bcrypt
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def signup_user(username: str, password: str) -> tuple[bool, str]:
    """
    Sign up a new user.
    Returns (success: bool, message: str)
    """
    # Check if user already exists
    existing_user = get_user(username)
    if existing_user:
        return False, "Username already exists"
    
    # Hash password and create user
    hashed_password = hash_password(password)
    try:
        create_user(username, hashed_password)
        return True, "Account created successfully"
    except Exception as e:
        return False, f"Error creating account: {str(e)}"

def login_user(username: str, password: str) -> tuple[bool, str, object]:
    """
    Log in a user.
    Returns (success: bool, message: str, user: User or None)
    """
    user = get_user(username)
    if not user:
        return False, "Invalid username or password", None
    
    if not verify_password(password, user.hashed_password):
        return False, "Invalid username or password", None
    
    return True, "Login successful", user
