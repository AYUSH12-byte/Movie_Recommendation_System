from app.database.database import (
    users_collection,
    movies_collection,
    ratings_collection
)


def create_indexes():

    # Users

    users_collection.create_index(
        "email",
        unique=True
    )

    # Movies

    movies_collection.create_index(
        "movieId",
        unique=True
    )

    # Ratings

    ratings_collection.create_index(
        [
            ("userId", 1),
            ("movieId", 1)
        ],
        unique=True
    )

    ratings_collection.create_index(
        "movieId"
    )

    ratings_collection.create_index(
        "createdAt"
    )

    print(
        "MongoDB indexes created successfully."
    )