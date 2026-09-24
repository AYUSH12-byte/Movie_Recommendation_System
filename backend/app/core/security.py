import os

from datetime import datetime, timedelta, timezone

import bcrypt
from dotenv import load_dotenv
from jose import jwt


load_dotenv()


JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "development-secret-key"
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

JWT_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_EXPIRE_MINUTES",
        "1440"
    )
)


# PASSWORD HASHING

def hash_password(password: str) -> str:

    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(
        password_bytes,
        salt
    )

    return hashed_password.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    plain_password_bytes = plain_password.encode(
        "utf-8"
    )

    hashed_password_bytes = hashed_password.encode(
        "utf-8"
    )

    return bcrypt.checkpw(
        plain_password_bytes,
        hashed_password_bytes
    )

# JWT TOKEN

def create_access_token(
    user_id: str
) -> str:

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=JWT_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token