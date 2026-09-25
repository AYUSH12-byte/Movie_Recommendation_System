import os
import random

import numpy as np
import pandas as pd

from recommender import MovieRecommender


MOVIES_FILE = "dataset/movies.csv"
RATINGS_FILE = "dataset/ratings.csv"

RESULTS_FILE = "evaluation_results_v2.csv"

SEED = 42

TOP_K_VALUES = [5, 10, 20]

MIN_USER_RATINGS = 5
MIN_TRAIN_RATINGS = 3

TEST_RATIO = 0.20

MAX_USERS = 100

LIKE_THRESHOLD = 4.0


random.seed(SEED)
np.random.seed(SEED)


def load_data():

    print("\nLoading datasets...")

    if not os.path.exists(MOVIES_FILE):
        raise FileNotFoundError(
            f"Movies dataset not found: {MOVIES_FILE}"
        )

    if not os.path.exists(RATINGS_FILE):
        raise FileNotFoundError(
            f"Ratings dataset not found: {RATINGS_FILE}"
        )

    movies = pd.read_csv(MOVIES_FILE)

    ratings = pd.read_csv(RATINGS_FILE)

    # Validate movie columns

    required_movie_columns = {
        "movieId",
        "title",
        "genres"
    }

    missing_movie_columns = (
        required_movie_columns
        - set(movies.columns)
    )

    if missing_movie_columns:

        raise ValueError(
            "Movies dataset is missing columns: "
            f"{missing_movie_columns}"
        )

    # Validate rating columns

    required_rating_columns = {
        "userId",
        "movieId",
        "rating"
    }

    missing_rating_columns = (
        required_rating_columns
        - set(ratings.columns)
    )

    if missing_rating_columns:

        raise ValueError(
            "Ratings dataset is missing columns: "
            f"{missing_rating_columns}"
        )

    # Clean data types

    movies["movieId"] = pd.to_numeric(
        movies["movieId"],
        errors="coerce"
    )

    ratings["userId"] = pd.to_numeric(
        ratings["userId"],
        errors="coerce"
    )

    ratings["movieId"] = pd.to_numeric(
        ratings["movieId"],
        errors="coerce"
    )

    ratings["rating"] = pd.to_numeric(
        ratings["rating"],
        errors="coerce"
    )

    # Remove invalid rows

    movies = movies.dropna(
        subset=["movieId"]
    ).copy()

    ratings = ratings.dropna(
        subset=[
            "userId",
            "movieId",
            "rating"
        ]
    ).copy()

    # Convert IDs to integers

    movies["movieId"] = (
        movies["movieId"]
        .astype(int)
    )

    ratings["userId"] = (
        ratings["userId"]
        .astype(int)
    )

    ratings["movieId"] = (
        ratings["movieId"]
        .astype(int)
    )

    # Keep ratings within MovieLens range

    ratings = ratings[
        (ratings["rating"] >= 0.5)
        & (ratings["rating"] <= 5.0)
    ].copy()

    print(
        f"Movies loaded: {len(movies):,}"
    )

    print(
        f"Ratings loaded: {len(ratings):,}"
    )

    return movies, ratings


def prepare_users(ratings):

    print("\nPreparing user train/test splits...")

    user_groups = []

    total_users = ratings["userId"].nunique()

    print(
        f"Total users in dataset: {total_users:,}"
    )

    # Process each user

    for user_id, user_ratings in ratings.groupby("userId"):

        user_ratings = user_ratings.copy()

        # Minimum rating requirement

        if len(user_ratings) < MIN_USER_RATINGS:
            continue

        # Highly-rated movies are considered relevant

        liked_movies = user_ratings[
            user_ratings["rating"] >= LIKE_THRESHOLD
        ].copy()

        # Need at least two relevant movies so that we can
        # create a meaningful train/test split.

        if len(liked_movies) < 2:
            continue

        # Calculate test size

        test_size = max(
            1,
            int(
                np.ceil(
                    len(liked_movies)
                    * TEST_RATIO
                )
            )
        )

        # Preserve minimum training ratings

        max_test_size = (
            len(user_ratings)
            - MIN_TRAIN_RATINGS
        )

        if max_test_size < 1:
            continue

        test_size = min(
            test_size,
            max_test_size,
            len(liked_movies)
        )

        if test_size < 1:
            continue

        # Randomly select relevant test movies

        user_seed = (
            SEED
            + int(user_id)
        )

        test_ratings = liked_movies.sample(
            n=test_size,
            random_state=user_seed
        )

        test_movie_ids = set(
            test_ratings["movieId"]
            .astype(int)
            .tolist()
        )

        # Remove test movies from training data

        train_ratings = user_ratings[
            ~user_ratings["movieId"].isin(
                test_movie_ids
            )
        ].copy()

        # Final training-size validation

        if len(train_ratings) < MIN_TRAIN_RATINGS:
            continue

        user_groups.append(
            {
                "userId": int(user_id),
                "train_ratings": train_ratings,
                "test_movie_ids": test_movie_ids
            }
        )

    # Shuffle users

    random.shuffle(user_groups)

    # Limit evaluation users

    if MAX_USERS is not None:

        user_groups = user_groups[
            :MAX_USERS
        ]

    print(
        f"Eligible users: {len(user_groups):,}"
    )

    return user_groups


def precision_at_k(
    recommended_ids,
    relevant_ids,
    k
):

    if k <= 0:
        return 0.0

    recommended = list(
        recommended_ids[:k]
    )

    if not recommended:
        return 0.0

    recommended_set = set(
        recommended
    )

    relevant_set = set(
        relevant_ids
    )

    hits = len(
        recommended_set
        .intersection(relevant_set)
    )

    return hits / len(recommended)


def recall_at_k(
    recommended_ids,
    relevant_ids,
    k
):

    if not relevant_ids:
        return 0.0

    recommended = list(
        recommended_ids[:k]
    )

    recommended_set = set(
        recommended
    )

    relevant_set = set(
        relevant_ids
    )

    hits = len(
        recommended_set
        .intersection(relevant_set)
    )

    return hits / len(relevant_set)


def hit_rate_at_k(
    recommended_ids,
    relevant_ids,
    k
):

    if not relevant_ids:
        return 0.0

    recommended = set(
        recommended_ids[:k]
    )

    relevant = set(
        relevant_ids
    )

    if recommended.intersection(
        relevant
    ):
        return 1.0

    return 0.0


def f1_at_k(
    precision,
    recall
):

    if (
        precision + recall
        == 0
    ):
        return 0.0

    return (
        2
        * precision
        * recall
        / (precision + recall)
    )


def get_content_recommendations(
    recommender,
    train_ratings,
    number_of_recommendations
):

    # Select liked movies

    liked_movies = train_ratings[
        train_ratings["rating"]
        >= LIKE_THRESHOLD
    ].sort_values(
        "rating",
        ascending=False
    )

    recommendation_scores = {}

    # Generate recommendations from each liked movie

    for _, rating_row in liked_movies.iterrows():

        movie_id = int(
            rating_row["movieId"]
        )

        movie = recommender.get_movie_by_id(
            movie_id
        )

        if movie is None:
            continue

        movie_title = movie["title"]

        recommendations = (
            recommender.recommend(
                movie_title,
                number_of_recommendations=(
                    number_of_recommendations
                )
            )
        )

        if not recommendations:
            continue

        # Accumulate similarity scores

        for recommendation in recommendations:

            recommended_movie_id = int(
                recommendation["movieId"]
            )

            similarity = float(
                recommendation.get(
                    "similarity_score",
                    0.0
                )
            )

            rating_value = float(
                rating_row["rating"]
            )

            score = (
                similarity
                * rating_value
            )

            if (
                recommended_movie_id
                not in recommendation_scores
            ):

                recommendation_scores[
                    recommended_movie_id
                ] = 0.0

            recommendation_scores[
                recommended_movie_id
            ] += score

    # Remove already-rated movies

    rated_movie_ids = set(
        train_ratings["movieId"]
        .astype(int)
        .tolist()
    )

    # Rank recommendations

    ranked = sorted(
        recommendation_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    result = []

    for movie_id, score in ranked:

        if movie_id in rated_movie_ids:
            continue

        result.append(
            int(movie_id)
        )

        if (
            len(result)
            >= number_of_recommendations
        ):
            break

    return result


def get_hybrid_recommendations(
    recommender,
    train_ratings,
    number_of_recommendations
):

    try:

        recommendations = (
            recommender.recommend_for_user(
                train_ratings,
                number_of_recommendations=(
                    number_of_recommendations
                )
            )
        )

    except Exception as error:

        print(
            "Hybrid recommendation error: "
            f"{error}"
        )

        return []

    if not recommendations:
        return []

    # Remove movies already rated by user

    rated_movie_ids = set(
        train_ratings["movieId"]
        .astype(int)
        .tolist()
    )

    result = []

    for recommendation in recommendations:

        try:

            movie_id = int(
                recommendation["movieId"]
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            continue

        if movie_id in rated_movie_ids:
            continue

        result.append(
            movie_id
        )

        if (
            len(result)
            >= number_of_recommendations
        ):
            break

    return result


def evaluate_user(
    recommender,
    user_data,
    model_name
):

    train_ratings = (
        user_data["train_ratings"]
    )

    test_movie_ids = (
        user_data["test_movie_ids"]
    )

    results = []

    max_k = max(
        TOP_K_VALUES
    )

    # Generate recommendations

    if model_name == "Content-Based":

        recommendations = (
            get_content_recommendations(
                recommender,
                train_ratings,
                max_k
            )
        )

    elif model_name == "Hybrid":

        recommendations = (
            get_hybrid_recommendations(
                recommender,
                train_ratings,
                max_k
            )
        )

    else:

        raise ValueError(
            f"Unknown model: {model_name}"
        )

    # Calculate metrics

    for k in TOP_K_VALUES:

        precision = precision_at_k(
            recommendations,
            test_movie_ids,
            k
        )

        recall = recall_at_k(
            recommendations,
            test_movie_ids,
            k
        )

        hit_rate = hit_rate_at_k(
            recommendations,
            test_movie_ids,
            k
        )

        f1 = f1_at_k(
            precision,
            recall
        )

        results.append(
            {
                "userId": user_data[
                    "userId"
                ],

                "model": model_name,

                "k": k,

                "precision": precision,

                "recall": recall,

                "hit_rate": hit_rate,

                "f1": f1,

                "train_ratings": len(
                    train_ratings
                ),

                "test_relevant_movies": len(
                    test_movie_ids
                ),

                "recommendation_count": len(
                    recommendations
                )
            }
        )

    return results


def evaluate_model():

    print("=" * 70)

    print(
        "MOVIE RECOMMENDATION SYSTEM"
    )

    print(
        "STRONGER MODEL EVALUATION V2"
    )

    print("=" * 70)

    # Load data

    movies, ratings = load_data()

    # Prepare users

    users = prepare_users(
        ratings
    )

    if not users:

        raise ValueError(
            "No eligible users found for evaluation."
        )

    # Initialize recommender
    #
    # IMPORTANT:
    # Your current MovieRecommender constructor does not
    # accept movies_file= and ratings_file= keyword arguments.
    #
    # Therefore we use positional arguments.

    print(
        "\nInitializing recommender..."
    )

    recommender = MovieRecommender(
        MOVIES_FILE,
        RATINGS_FILE
    )

    print(
        "Recommender initialized successfully."
    )

    # Models to evaluate

    models = [
        "Content-Based",
        "Hybrid"
    ]

    all_results = []

    # Evaluate each model

    for model_name in models:

        print("\n" + "-" * 70)

        print(
            f"Evaluating: {model_name}"
        )

        print("-" * 70)

        for index, user_data in enumerate(
            users
        ):

            try:

                user_results = (
                    evaluate_user(
                        recommender,
                        user_data,
                        model_name
                    )
                )

                all_results.extend(
                    user_results
                )

            except Exception as error:

                print(
                    f"Warning: User "
                    f"{user_data['userId']} "
                    f"failed: {error}"
                )

            processed = index + 1

            if (
                processed % 10 == 0
                or processed == len(users)
            ):

                print(
                    f"Processed "
                    f"{processed}/"
                    f"{len(users)} users"
                )

    # Create DataFrame

    results_df = pd.DataFrame(
        all_results
    )

    if results_df.empty:

        raise ValueError(
            "Evaluation produced no results."
        )

    # Save raw results

    results_df.to_csv(
        RESULTS_FILE,
        index=False
    )

    print(
        "\nEvaluation completed successfully."
    )

    print(
        f"Results saved to: "
        f"{RESULTS_FILE}"
    )

    return results_df


def print_summary(
    results_df
):

    print("\n")

    print("=" * 70)

    print(
        "EVALUATION SUMMARY"
    )

    print("=" * 70)

    # Average metrics

    summary = (
        results_df
        .groupby(
            [
                "model",
                "k"
            ]
        )[
            [
                "precision",
                "recall",
                "hit_rate",
                "f1"
            ]
        ]
        .mean()
        .reset_index()
    )

    # Print each model

    for model_name in [
        "Content-Based",
        "Hybrid"
    ]:

        model_results = summary[
            summary["model"]
            == model_name
        ]

        print(
            f"\nModel: {model_name}"
        )

        print(
            "-" * 50
        )

        for _, row in (
            model_results
            .sort_values("k")
            .iterrows()
        ):

            k = int(
                row["k"]
            )

            print(
                f"\nK = {k}"
            )

            print(
                f"Precision@{k}: "
                f"{row['precision']:.4f}"
            )

            print(
                f"Recall@{k}: "
                f"{row['recall']:.4f}"
            )

            print(
                f"Hit Rate@{k}: "
                f"{row['hit_rate']:.4f}"
            )

            print(
                f"F1@{k}: "
                f"{row['f1']:.4f}"
            )

    # Evaluation information

    print("\n")

    print(
        "Evaluation configuration:"
    )

    print(
        f"Eligible users evaluated: "
        f"{results_df['userId'].nunique()}"
    )

    print(
        f"Test ratio: "
        f"{TEST_RATIO * 100:.0f}%"
    )

    print(
        f"Minimum training ratings: "
        f"{MIN_TRAIN_RATINGS}"
    )

    print(
        f"Like threshold: "
        f"{LIKE_THRESHOLD}"
    )

    print(
        f"Top-K values: "
        f"{TOP_K_VALUES}"
    )

    print(
        f"Random seed: "
        f"{SEED}"
    )

    print(
        "\n" + "=" * 70
    )


def save_summary(
    results_df
):

    summary_file = (
        "evaluation_summary_v2.csv"
    )

    summary = (
        results_df
        .groupby(
            [
                "model",
                "k"
            ]
        )[
            [
                "precision",
                "recall",
                "hit_rate",
                "f1"
            ]
        ]
        .mean()
        .reset_index()
    )

    summary.to_csv(
        summary_file,
        index=False
    )

    print(
        f"\nSummary saved to: "
        f"{summary_file}"
    )

    return summary


def main():

    try:

        results = evaluate_model()

        print_summary(
            results
        )

        save_summary(
            results
        )

    except FileNotFoundError as error:

        print(
            "\nFile error:"
        )

        print(
            error
        )

    except ValueError as error:

        print(
            "\nData/Evaluation error:"
        )

        print(
            error
        )

    except Exception as error:

        print(
            "\nUnexpected error:"
        )

        print(
            error
        )

        raise


if __name__ == "__main__":

    main()