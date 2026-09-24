from app.database.database import (
    users_collection,
    movies_collection,
    ratings_collection
)


def create_indexes():

    # User email must be unique
    users_collection.create_index(
        "email",
        unique=True
    )

    # Movie ID must be unique
    movies_collection.create_index(
        "movieId",
        unique=True
    )

    # One user can rate one movie only once
    ratings_collection.create_index(
        [
            ("userId", 1),
            ("movieId", 1)
        ],
        unique=True
    )

    print("MongoDB indexes created successfully.")