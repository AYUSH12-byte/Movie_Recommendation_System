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


# DATASET PATH

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "movies.csv"
)


# INITIALIZE RECOMMENDER

recommender = MovieRecommender(
    DATASET_PATH
)


# CONTENT-BASED RECOMMENDATIONS

def get_movie_recommendations(
    movie_title: str,
    limit: int = 10
):

    recommendations = recommender.recommend(
        movie_title=movie_title,
        number_of_recommendations=limit
    )

    return recommendations


# PERSONALIZED RECOMMENDATIONS

def get_personalized_recommendations(
    user_id: str,
    ratings: list,
    limit: int = 10
):

    # Check user rating history

    if not ratings:

        return {
            "success": True,
            "hasProfile": False,
            "message": (
                "Rate some movies to get "
                "personalized recommendations."
            ),
            "recommendations": []
        }

    # Convert MongoDB ratings to DataFrame

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
                "message": (
                    f"Missing required rating field: "
                    f"{column}"
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

    # Generate recommendations

    recommendations = (
        recommender.recommend_for_user(
            user_id=user_id,
            ratings=ratings_df,
            number_of_recommendations=limit
        )
    )

    # Add human-readable explanation

    for recommendation in recommendations:

        source_title = recommendation.get(
            "sourceMovieTitle"
        )

        source_rating = recommendation.get(
            "sourceUserRating"
        )

        similarity = recommendation.get(
            "similarity_score",
            0
        )

        if source_title and source_rating:

            recommendation["reason"] = (
                f"Recommended because you rated "
                f"{source_title} "
                f"{source_rating}/5, and this movie "
                f"has a content similarity score of "
                f"{similarity} with it."
            )

        else:

            recommendation["reason"] = (
                "Recommended based on similarity "
                "with movies you rated highly."
            )

    return {
        "success": True,
        "hasProfile": True,
        "message": (
            "Personalized recommendations "
            "generated successfully."
        ),
        "recommendations": recommendations
    }