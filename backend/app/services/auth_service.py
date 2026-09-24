from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from app.database.database import users_collection
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


def register_user(
    name: str,
    email: str,
    password: str
):

    email = email.lower().strip()

    existing_user = users_collection.find_one({
        "email": email
    })

    if existing_user:
        return {
            "success": False,
            "message": "Email already registered"
        }

    user = {
        "name": name.strip(),
        "email": email,
        "password": hash_password(password),
        "createdAt": datetime.now(timezone.utc)
    }

    try:

        result = users_collection.insert_one(user)

    except DuplicateKeyError:

        return {
            "success": False,
            "message": "Email already registered"
        }

    user_id = str(result.inserted_id)

    token = create_access_token(
        user_id
    )

    return {
        "success": True,
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user_id,
            "name": user["name"],
            "email": user["email"]
        }
    }


def login_user(
    email: str,
    password: str
):

    email = email.lower().strip()

    user = users_collection.find_one({
        "email": email
    })

    if not user:

        return {
            "success": False,
            "message": "Invalid email or password"
        }

    password_valid = verify_password(
        password,
        user["password"]
    )

    if not password_valid:

        return {
            "success": False,
            "message": "Invalid email or password"
        }

    token = create_access_token(
        str(user["_id"])
    )

    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"]
        }
    }