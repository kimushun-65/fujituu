from passlib.context import CryptContext
import base64
import binascii

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def decode_basic_auth(auth_header: str) -> tuple[str, str]:
    try:
        if not auth_header.startswith("Basic "):
            raise ValueError("Invalid authorization header format")
        
        encoded_credentials = auth_header.split(" ", 1)[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        user_id, password = decoded_credentials.split(":", 1)
        return user_id, password
    except (binascii.Error, UnicodeDecodeError, ValueError):
        raise ValueError("Invalid authorization header")