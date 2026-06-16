from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# HASH PASSWORD
def hash_password(password):

    return pwd_context.hash(password)

# VERIFY PASSWORD
def verify_password(plain, hashed):

    return pwd_context.verify(plain, hashed)

# CREATE JWT TOKEN
def create_token(data):

    payload = data.copy()

    expire = datetime.utcnow() + timedelta(days=1)

    payload.update({
        "exp": expire
    })

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

