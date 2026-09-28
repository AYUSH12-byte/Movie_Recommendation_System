from app.database.database import (
    movies_collection,
    ratings_collection
)

from app.services.tmdb_service import (
    search_tmdb_movie
)


# ENRICH MOVIE WITH TMDB DATA

def enrich_movie_with_tmdb(movie):
    """
    Add TMDB metadata to a movie.

    TMDB provides:
    - TMDB ID
    - Poster
    - Backdrop
    - Overview
    - Release date
    - TMDB rating
    - TMDB vote count
    """

    if not movie:
        return movie

    movie = dict(movie)

    tmdb_data = search_tmdb_movie(
        movie.get("title", "")
    )

    if tmdb_data:
        movie.update(
            tmdb_data
        )

    return movie


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
        #
        # Formula:
        #
        # averageRating × ln(totalRatings + 1)

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

        # Add TMDB metadata

        movie = enrich_movie_with_tmdb(
            movie
        )

        # Build response

        results.append({
            "movieId": movie_id,

            "title": movie.get(
                "title",
                ""
            ),

            "genres": movie.get(
                "genres",
                ""
            ),

            # TMDB data

            "tmdbId": movie.get(
                "tmdbId"
            ),

            "posterUrl": movie.get(
                "posterUrl"
            ),

            "backdropUrl": movie.get(
                "backdropUrl"
            ),

            "overview": movie.get(
                "overview",
                ""
            ),

            "releaseDate": movie.get(
                "releaseDate",
                ""
            ),

            "tmdbRating": movie.get(
                "tmdbRating"
            ),

            "tmdbVoteCount": movie.get(
                "tmdbVoteCount"
            ),

            # Recommendation/popularity data

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
        #
        # Formula:
        #
        # averageRating × recentRatings

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

        # Limit results

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

        # Add TMDB metadata

        movie = enrich_movie_with_tmdb(
            movie
        )

        # Build response

        results.append({
            "movieId": movie_id,

            "title": movie.get(
                "title",
                ""
            ),

            "genres": movie.get(
                "genres",
                ""
            ),

            # TMDB data

            "tmdbId": movie.get(
                "tmdbId"
            ),

            "posterUrl": movie.get(
                "posterUrl"
            ),

            "backdropUrl": movie.get(
                "backdropUrl"
            ),

            "overview": movie.get(
                "overview",
                ""
            ),

            "releaseDate": movie.get(
                "releaseDate",
                ""
            ),

            "tmdbRating": movie.get(
                "tmdbRating"
            ),

            "tmdbVoteCount": movie.get(
                "tmdbVoteCount"
            ),

            # Trending data

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