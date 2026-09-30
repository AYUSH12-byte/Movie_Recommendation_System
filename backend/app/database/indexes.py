from app.database.database import (
    users_collection,
    movies_collection,
    ratings_collection
)


def create_indexes():

    # USERS

    users_collection.create_index(
        "email",
        unique=True
    )


    # MOVIES

    movies_collection.create_index(
        "movieId",
        unique=True
    )

    movies_collection.create_index(
        "tmdbId"
    )


    # RATINGS

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