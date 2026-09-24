import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# Load environment variables
load_dotenv()


MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://127.0.0.1:27017"
)

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "movie_recommendation_db"
)


# MongoDB client
client = MongoClient(MONGO_URI)


# Database
db = client[DATABASE_NAME]


# Collections
users_collection = db["users"]
movies_collection = db["movies"]
ratings_collection = db["ratings"]


def get_database():
    return db


def check_database_connection():
    try:
        client.admin.command("ping")

        return {
            "connected": True,
            "database": DATABASE_NAME
        }

    except PyMongoError as error:
        return {
            "connected": False,
            "error": str(error)
        }