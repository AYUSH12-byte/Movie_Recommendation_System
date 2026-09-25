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

    sys.path.append(
        BASE_DIR
    )


from recommender import MovieRecommender


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
    dataset_path=DATASET_PATH,
    ratings_path=RATINGS_PATH
)


# CONTENT-BASED RECOMMENDATION

def get_movie_recommendations(
    movie_title: str,
    limit: int = 10
):

    return recommender.recommend(
        movie_title=movie_title,
        number_of_recommendations=limit
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

    # No ratings

    if not ratings:

        return get_cold_start_recommendations(
            limit=limit
        )

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

    # Normalize data types

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

    # Check whether user has enough liked movies

    user_ratings = ratings_df[
        ratings_df["userId"]
        == str(user_id)
    ]

    liked_movies = user_ratings[
        user_ratings["rating"] >= 4.0
    ]

    # No useful preference profile

    if liked_movies.empty:

        return get_cold_start_recommendations(
            limit=limit
        )

    # Generate hybrid recommendations

    recommendations = (
        recommender.recommend_for_user(
            user_id=user_id,
            ratings=ratings_df,
            number_of_recommendations=limit
        )
    )

    # Safety fallback

    if not recommendations:

        return get_cold_start_recommendations(
            limit=limit
        )

    # Add explanations

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
            and
            source_rating
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