from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "supersecretkey"  # Use a strong key and keep it secret!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    """Create a JWT token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    """Verify the JWT token and return the decoded data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
def check_role(user_role: str, required_role: str):
    """Check if the user has the required role."""
    if user_role != required_role:
        raise Exception("Access Denied: Insufficient Role")

