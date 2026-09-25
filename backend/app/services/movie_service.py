from app.database.database import (
    movies_collection,
    ratings_collection
)


# GET POPULAR MOVIES

def get_popular_movies(
    limit: int = 10,
    minimum_ratings: int = 3
):
    """
    Return popular movies using a weighted popularity score.

    Movies are ranked using:
    - Average rating
    - Number of ratings
    """

    # Aggregate ratings by movie

    pipeline = [
        {
            "$group": {
                "_id": "$movieId",
                "averageRating": {
                    "$avg": "$rating"
                },
                "totalRatings": {
                    "$sum": 1
                }
            }
        },

        # Only include movies with enough ratings

        {
            "$match": {
                "totalRatings": {
                    "$gte": minimum_ratings
                }
            }
        },

        # Calculate popularity score

        {
            "$addFields": {
                "popularityScore": {
                    "$multiply": [
                        "$averageRating",
                        {
                            "$ln": {
                                "$add": [
                                    "$totalRatings",
                                    1
                                ]
                            }
                        }
                    ]
                }
            }
        },

        # Sort by popularity

        {
            "$sort": {
                "popularityScore": -1
            }
        },

        # Limit results

        {
            "$limit": limit
        }
    ]

    popular_movies = list(
        ratings_collection.aggregate(
            pipeline
        )
    )

    # Get movie details

    results = []

    for item in popular_movies:

        movie_id = int(
            item["_id"]
        )

        movie = movies_collection.find_one(
            {
                "movieId": movie_id
            },
            {
                "_id": 0
            }
        )

        if not movie:
            continue

        results.append({
            "movieId": movie_id,
            "title": movie["title"],
            "genres": movie.get(
                "genres",
                ""
            ),
            "averageRating": round(
                float(
                    item["averageRating"]
                ),
                2
            ),
            "totalRatings": int(
                item["totalRatings"]
            ),
            "popularityScore": round(
                float(
                    item["popularityScore"]
                ),
                4
            )
        })

    return results


# GET TRENDING MOVIES

def get_trending_movies(
    limit: int = 10,
    days: int = 30
):
    """
    Return movies receiving recent ratings.

    Trending movies are based on ratings submitted
    within the selected number of days.
    """

    from datetime import (
        datetime,
        timedelta,
        timezone
    )

    # Calculate date threshold

    threshold = (
        datetime.now(
            timezone.utc
        )
        - timedelta(
            days=days
        )
    )

    # Aggregate recent ratings

    pipeline = [
        {
            "$match": {
                "createdAt": {
                    "$gte": threshold
                }
            }
        },

        {
            "$group": {
                "_id": "$movieId",
                "averageRating": {
                    "$avg": "$rating"
                },
                "recentRatings": {
                    "$sum": 1
                }
            }
        },

        # Calculate trending score

        {
            "$addFields": {
                "trendingScore": {
                    "$multiply": [
                        "$averageRating",
                        "$recentRatings"
                    ]
                }
            }
        },

        # Sort by trending score

        {
            "$sort": {
                "trendingScore": -1
            }
        },

        {
            "$limit": limit
        }
    ]

    trending_movies = list(
        ratings_collection.aggregate(
            pipeline
        )
    )

    # Get movie details

    results = []

    for item in trending_movies:

        movie_id = int(
            item["_id"]
        )

        movie = movies_collection.find_one(
            {
                "movieId": movie_id
            },
            {
                "_id": 0
            }
        )

        if not movie:
            continue

        results.append({
            "movieId": movie_id,
            "title": movie["title"],
            "genres": movie.get(
                "genres",
                ""
            ),
            "averageRating": round(
                float(
                    item["averageRating"]
                ),
                2
            ),
            "recentRatings": int(
                item["recentRatings"]
            ),
            "trendingScore": round(
                float(
                    item["trendingScore"]
                ),
                4
            )
        })

    return results