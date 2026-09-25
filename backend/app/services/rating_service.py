from datetime import datetime, timezone

from bson import ObjectId

from app.database.database import (
    ratings_collection,
    movies_collection
)

# RECALCULATE MOVIE RATING

def update_movie_rating(movie_id: int):

    ratings = list(
        ratings_collection.find(
            {
                "movieId": movie_id
            }
        )
    )

    total_ratings = len(ratings)

    if total_ratings == 0:

        average_rating = 0.0

    else:

        total = sum(
            rating["rating"]
            for rating in ratings
        )

        average_rating = round(
            total / total_ratings,
            2
        )

    movies_collection.update_one(
        {
            "movieId": movie_id
        },
        {
            "$set": {
                "averageRating": average_rating,
                "totalRatings": total_ratings
            }
        }
    )

    return {
        "averageRating": average_rating,
        "totalRatings": total_ratings
    }
# ADD OR UPDATE RATING

def create_or_update_rating(
    user_id: str,
    movie_id: int,
    rating: float
):

    movie = movies_collection.find_one(
        {
            "movieId": movie_id
        }
    )

    if not movie:

        return {
            "success": False,
            "message": "Movie not found"
        }

    existing_rating = ratings_collection.find_one(
        {
            "userId": user_id,
            "movieId": movie_id
        }
    )

    now = datetime.now(
        timezone.utc
    )

    if existing_rating:

        ratings_collection.update_one(
            {
                "_id": existing_rating["_id"]
            },
            {
                "$set": {
                    "rating": rating,
                    "updatedAt": now
                }
            }
        )

        message = "Rating updated successfully"

        rating_id = str(
            existing_rating["_id"]
        )

    else:

        result = ratings_collection.insert_one(
            {
                "userId": user_id,
                "movieId": movie_id,
                "rating": rating,
                "createdAt": now,
                "updatedAt": now
            }
        )

        message = "Rating added successfully"

        rating_id = str(
            result.inserted_id
        )

    movie_rating = update_movie_rating(
        movie_id
    )

    return {
        "success": True,
        "message": message,
        "rating": {
            "id": rating_id,
            "userId": user_id,
            "movieId": movie_id,
            "rating": rating
        },
        "movie": movie_rating
    }

# GET USER RATINGS

def get_user_ratings(
    user_id: str
):

    ratings = list(
        ratings_collection.find(
            {
                "userId": user_id
            },
            {
                "_id": 1,
                "userId": 1,
                "movieId": 1,
                "rating": 1,
                "createdAt": 1,
                "updatedAt": 1
            }
        ).sort(
            "updatedAt",
            -1
        )
    )

    result = []

    for item in ratings:

        result.append(
            {
                "id": str(
                    item["_id"]
                ),
                "userId": item["userId"],
                "movieId": item["movieId"],
                "rating": item["rating"],
                "createdAt": item["createdAt"],
                "updatedAt": item["updatedAt"]
            }
        )

    return result

# GET USER'S RATING FOR ONE MOVIE

def get_user_movie_rating(
    user_id: str,
    movie_id: int
):

    rating = ratings_collection.find_one(
        {
            "userId": user_id,
            "movieId": movie_id
        }
    )

    if not rating:
        return None

    return {
        "id": str(
            rating["_id"]
        ),
        "userId": rating["userId"],
        "movieId": rating["movieId"],
        "rating": rating["rating"],
        "createdAt": rating["createdAt"],
        "updatedAt": rating["updatedAt"]
    }

# DELETE RATING

def delete_rating(
    user_id: str,
    movie_id: int
):

    result = ratings_collection.delete_one(
        {
            "userId": user_id,
            "movieId": movie_id
        }
    )

    if result.deleted_count == 0:

        return {
            "success": False,
            "message": "Rating not found"
        }

    movie_rating = update_movie_rating(
        movie_id
    )

    return {
        "success": True,
        "message": "Rating deleted successfully",
        "movie": movie_rating
    }