# app/auth.py

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt


# Load the .env file
load_dotenv()

# Now you can access the SECRET_KEY from the environment
SECRET_KEY = os.getenv("SECRET_KEY")

# Example usage in JWT creation

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expiration = payload.get("exp")
        if expiration and datetime.utcfromtimestamp(expiration) < datetime.utcnow():
            return None  # Token has expired
        return payload
    except JWTError:
        return None  # Invalid token]
