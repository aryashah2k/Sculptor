"""Mock payment system for testing without Stripe integration."""
import os
from dotenv import load_dotenv
from database import add_credits

load_dotenv()

def verify_payment_password(password: str) -> bool:
    """
    Verify the payment password against SECRET_KEY in .env file.
    Returns True if password matches.
    """
    secret_key = os.getenv('SECRET_KEY', 'sculptor')
    return password == secret_key

def simulate_payment_success(user_id: int, password: str, credits: int = 10) -> tuple[bool, str]:
    """
    Simulate a successful payment after password verification.
    Returns (success: bool, message: str)
    """
    # Verify password first
    if not verify_payment_password(password):
        return False, "Invalid payment password"
    
    # Add credits if password is correct
    try:
        add_credits(user_id, credits)
        return True, f"Successfully added {credits} credits"
    except Exception as e:
        return False, f"Failed to add credits: {str(e)}"
