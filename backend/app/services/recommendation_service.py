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


# DATASET

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "movies.csv"
)


# INITIALIZE RECOMMENDER

recommender = MovieRecommender(
    DATASET_PATH
)


# CONTENT-BASED RECOMMENDATION

def get_movie_recommendations(
    movie_title: str,
    limit: int = 10
):
    recommendations = recommender.recommend(
        movie_title,
        limit
    )

    return recommendations


# PERSONALIZED RECOMMENDATION

def get_personalized_recommendations(
    user_id: str,
    ratings: list,
    limit: int = 10
):
    """
    Generate personalized movie recommendations
    based on the user's MongoDB ratings.
    """

    # Check whether user has ratings

    if not ratings:
        return {
            "success": True,
            "hasProfile": False,
            "message": (
                "Rate some movies to get personalized "
                "recommendations."
            ),
            "recommendations": []
        }

    # Convert MongoDB ratings into DataFrame

    ratings_df = pd.DataFrame(
        ratings
    )

    # Make sure required columns exist

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
                "message": (
                    f"Missing required rating field: {column}"
                ),
                "recommendations": []
            }

    # Ensure correct data types

    ratings_df["userId"] = (
        ratings_df["userId"]
        .astype(str)
    )

    ratings_df["movieId"] = (
        pd.to_numeric(
            ratings_df["movieId"],
            errors="coerce"
        )
    )

    ratings_df["rating"] = (
        pd.to_numeric(
            ratings_df["rating"],
            errors="coerce"
        )
    )

    # Remove invalid records

    ratings_df = ratings_df.dropna(
        subset=[
            "movieId",
            "rating"
        ]
    )

    # Generate recommendations

    recommendations = (
        recommender.recommend_for_user(
            user_id=user_id,
            ratings=ratings_df,
            number_of_recommendations=limit
        )
    )

    return {
        "success": True,
        "hasProfile": True,
        "message": (
            "Personalized recommendations generated successfully."
        ),
        "recommendations": recommendations
    }