import os
import sys

import pandas as pd


# ML MODEL PATH

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../ml-model"
    )
)

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


from recommender import MovieRecommender

from app.services.tmdb_service import (
    search_tmdb_movie
)


# DATASET PATHS

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "movies.csv"
)

RATINGS_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "ratings.csv"
)


# INITIALIZE RECOMMENDER

recommender = MovieRecommender(
    DATASET_PATH,
    RATINGS_PATH
)


# ADD TMDB METADATA

def enrich_recommendations_with_tmdb(
    recommendations
):
    """
    Add TMDB metadata to recommendation results.

    Adds:
    - tmdbId
    - posterUrl
    - backdropUrl
    - overview
    - releaseDate
    - tmdbRating
    - tmdbVoteCount
    """

    enriched_recommendations = []

    for recommendation in recommendations:

        recommendation = dict(
            recommendation
        )

        title = recommendation.get(
            "title",
            ""
        )

        if title:
            tmdb_data = search_tmdb_movie(
                title
            )

            if tmdb_data:
                recommendation.update(
                    tmdb_data
                )

        enriched_recommendations.append(
            recommendation
        )

    return enriched_recommendations


# CONTENT-BASED RECOMMENDATION

def get_movie_recommendations(
    movie_title: str,
    limit: int = 10
):

    recommendations = recommender.recommend(
        movie_title=movie_title,
        number_of_recommendations=limit
    )

    return enrich_recommendations_with_tmdb(
        recommendations
    )


# COLD-START RECOMMENDATIONS

def get_cold_start_recommendations(
    limit: int = 10
):

    recommendations = (
        recommender.get_cold_start_recommendations(
            number_of_recommendations=limit
        )
    )

    recommendations = (
        enrich_recommendations_with_tmdb(
            recommendations
        )
    )

    return {
        "success": True,
        "hasProfile": False,
        "recommendationType": "cold_start",

        "algorithm": {
            "method": (
                "Popularity-based cold-start "
                "recommendation"
            ),
            "minimumRatings": 10
        },

        "message": (
            "Popular movies are shown because "
            "there is not enough user rating "
            "history for personalized recommendations."
        ),

        "recommendations": recommendations
    }


# PERSONALIZED HYBRID RECOMMENDATION

def get_personalized_recommendations(
    user_id: str,
    ratings: list,
    limit: int = 10
):

    # NO RATINGS

    if not ratings:
        return get_cold_start_recommendations(
            limit=limit
        )


    # CREATE DATAFRAME

    ratings_df = pd.DataFrame(
        ratings
    )

    required_columns = [
        "userId",
        "movieId",
        "rating"
    ]

    for column in required_columns:

        if column not in ratings_df.columns:
            return {
                "success": False,
                "hasProfile": False,
                "recommendationType": "error",

                "message": (
                    f"Missing required rating "
                    f"field: {column}"
                ),

                "recommendations": []
            }


    # NORMALIZE DATA TYPES

    ratings_df["userId"] = (
        ratings_df["userId"]
        .astype(str)
    )

    ratings_df["movieId"] = pd.to_numeric(
        ratings_df["movieId"],
        errors="coerce"
    )

    ratings_df["rating"] = pd.to_numeric(
        ratings_df["rating"],
        errors="coerce"
    )

    ratings_df = ratings_df.dropna(
        subset=[
            "movieId",
            "rating"
        ]
    )


    # CHECK USER PROFILE

    user_ratings = ratings_df[
        ratings_df["userId"]
        == str(user_id)
    ]

    liked_movies = user_ratings[
        user_ratings["rating"] >= 4.0
    ]


    # NO USEFUL PREFERENCE PROFILE

    if liked_movies.empty:
        return get_cold_start_recommendations(
            limit=limit
        )


    # GENERATE HYBRID RECOMMENDATIONS

    recommendations = (
        recommender.recommend_for_user(
            user_id=user_id,
            ratings=ratings_df,
            number_of_recommendations=limit
        )
    )


    # SAFETY FALLBACK

    if not recommendations:
        return get_cold_start_recommendations(
            limit=limit
        )


    # ADD EXPLANATIONS

    for recommendation in recommendations:

        source_title = (
            recommendation.get(
                "sourceMovieTitle"
            )
        )

        source_rating = (
            recommendation.get(
                "sourceUserRating"
            )
        )

        similarity = (
            recommendation.get(
                "similarity_score",
                0
            )
        )

        popularity = (
            recommendation.get(
                "popularity_score",
                0
            )
        )

        diversity = (
            recommendation.get(
                "diversity_score",
                0
            )
        )

        if (
            source_title
            and source_rating
        ):
            recommendation["reason"] = (
                f"Recommended because you "
                f"rated {source_title} "
                f"{source_rating}/5. "

                f"The movie has a content "
                f"similarity score of "
                f"{similarity}, a popularity "
                f"score of {popularity}, and "
                f"a diversity-aware ranking "
                f"score of {diversity}."
            )

        else:
            recommendation["reason"] = (
                "Recommended based on your "
                "movie preferences, content "
                "similarity, popularity, and "
                "recommendation diversity."
            )


    # ADD TMDB METADATA

    recommendations = (
        enrich_recommendations_with_tmdb(
            recommendations
        )
    )


    # FINAL RESPONSE

    return {
        "success": True,

        "hasProfile": True,

        "recommendationType": "hybrid",

        "algorithm": {
            "contentWeight": 0.60,

            "preferenceWeight": 0.25,

            "popularityWeight": 0.15,

            "diversityWeight": 0.25
        },

        "message": (
            "Hybrid personalized recommendations "
            "generated successfully with "
            "diversity-aware reranking."
        ),

        "recommendations": recommendations
    }