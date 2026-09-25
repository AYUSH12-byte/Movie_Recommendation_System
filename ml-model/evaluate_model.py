import random

import pandas as pd

from recommender import MovieRecommender


# CONFIGURATION

DATASET_PATH = "dataset/movies.csv"
RATINGS_PATH = "dataset/ratings.csv"

K_VALUES = [5, 10, 20]

MIN_USER_RATINGS = 5

MAX_USERS = 100

RANDOM_SEED = 42


# PRECISION@K

def precision_at_k(
    recommended_movies,
    relevant_movies,
    k=10
):
    """
    Precision@K:

    Measures how many recommended movies
    are relevant among the top K results.
    """

    if not recommended_movies:
        return 0.0

    recommended_movies = (
        recommended_movies[:k]
    )

    recommended_ids = {
        int(movie["movieId"])
        for movie in recommended_movies
    }

    relevant_ids = {
        int(movie_id)
        for movie_id in relevant_movies
    }

    hits = (
        recommended_ids
        &
        relevant_ids
    )

    return (
        len(hits)
        /
        len(recommended_movies)
    )


# RECALL@K

def recall_at_k(
    recommended_movies,
    relevant_movies,
    k=10
):
    """
    Recall@K:

    Measures how many relevant movies
    were successfully recommended.
    """

    if not relevant_movies:
        return 0.0

    recommended_movies = (
        recommended_movies[:k]
    )

    recommended_ids = {
        int(movie["movieId"])
        for movie in recommended_movies
    }

    relevant_ids = {
        int(movie_id)
        for movie_id in relevant_movies
    }

    hits = (
        recommended_ids
        &
        relevant_ids
    )

    return (
        len(hits)
        /
        len(relevant_ids)
    )


# HIT RATE@K

def hit_rate_at_k(
    recommended_movies,
    relevant_movies,
    k=10
):
    """
    Hit Rate@K:

    Returns 1 if at least one relevant
    movie appears in the top K results.
    Otherwise returns 0.
    """

    if not recommended_movies:
        return 0.0

    recommended_movies = (
        recommended_movies[:k]
    )

    recommended_ids = {
        int(movie["movieId"])
        for movie in recommended_movies
    }

    relevant_ids = {
        int(movie_id)
        for movie_id in relevant_movies
    }

    return (
        1.0
        if recommended_ids.intersection(
            relevant_ids
        )
        else 0.0
    )


# CONTENT-BASED RECOMMENDATIONS

def get_content_recommendations(
    recommender,
    train_ratings,
    user_id,
    k
):
    """
    Generate content-based recommendations
    using movies liked by the user.
    """

    user_ratings = train_ratings[
        train_ratings["userId"] == user_id
    ]

    liked_movies = user_ratings[
        user_ratings["rating"] >= 4.0
    ]

    if liked_movies.empty:
        return []

    # Movies already seen by user
    rated_movie_ids = set(
        user_ratings["movieId"]
        .astype(int)
        .tolist()
    )

    recommendation_scores = {}

    # Generate recommendations from
    # each movie the user liked
    for _, rating_row in (
        liked_movies.iterrows()
    ):

        movie_id = int(
            rating_row["movieId"]
        )

        movie = recommender.get_movie_by_id(
            movie_id
        )

        if movie is None:
            continue

        recommendations = (
            recommender.recommend(
                movie_title=movie["title"],
                number_of_recommendations=(
                    k * 5
                )
            )
        )

        for recommendation in recommendations:

            recommended_movie_id = int(
                recommendation["movieId"]
            )

            # Don't recommend movies
            # already rated by the user.
            if (
                recommended_movie_id
                in rated_movie_ids
            ):
                continue

            similarity_score = float(
                recommendation.get(
                    "similarity_score",
                    0.0
                )
            )

            # Keep strongest similarity
            # if multiple liked movies
            # recommend the same movie.
            previous_score = (
                recommendation_scores.get(
                    recommended_movie_id,
                    0.0
                )
            )

            recommendation_scores[
                recommended_movie_id
            ] = max(
                previous_score,
                similarity_score
            )

    # Sort by similarity
    sorted_recommendations = sorted(
        recommendation_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    results = []

    for movie_id, score in (
        sorted_recommendations[:k]
    ):

        movie = recommender.get_movie_by_id(
            movie_id
        )

        if movie is None:
            continue

        results.append({
            "movieId": movie["movieId"],
            "title": movie["title"],
            "genres": movie["genres"],
            "similarity_score": round(
                float(score),
                4
            )
        })

    return results


# HYBRID RECOMMENDATIONS

def get_hybrid_recommendations(
    recommender,
    train_ratings,
    user_id,
    k
):
    """
    Generate recommendations using
    the hybrid recommendation engine.
    """

    recommendations = (
        recommender.recommend_for_user(
            user_id=user_id,
            ratings=train_ratings,
            number_of_recommendations=k
        )
    )

    return recommendations


# EVALUATE ONE USER

def evaluate_user(
    recommender,
    ratings,
    user_id,
    k
):
    """
    Evaluate one user.

    One liked movie is held out from the
    training data.

    The recommender must try to recover
    the hidden movie.
    """

    user_ratings = ratings[
        ratings["userId"] == user_id
    ].copy()

    if (
        len(user_ratings)
        < MIN_USER_RATINGS
    ):
        return None

    # Movies considered relevant
    liked_ratings = user_ratings[
        user_ratings["rating"] >= 4.0
    ]

    if liked_ratings.empty:
        return None

    # HOLD OUT ONE LIKED MOVIE

    test_rating = liked_ratings.sample(
        n=1,
        random_state=RANDOM_SEED
    )

    test_movie_id = int(
        test_rating.iloc[0]["movieId"]
    )

    relevant_movies = [
        test_movie_id
    ]

    # REMOVE TEST MOVIE FROM TRAINING DATA

    train_ratings = user_ratings[
        user_ratings["movieId"]
        != test_movie_id
    ].copy()

    # CONTENT-BASED

    content_recommendations = (
        get_content_recommendations(
            recommender=recommender,
            train_ratings=train_ratings,
            user_id=user_id,
            k=k
        )
    )

    content_precision = precision_at_k(
        content_recommendations,
        relevant_movies,
        k
    )

    content_recall = recall_at_k(
        content_recommendations,
        relevant_movies,
        k
    )

    content_hit_rate = hit_rate_at_k(
        content_recommendations,
        relevant_movies,
        k
    )

    # HYBRID

    hybrid_recommendations = (
        get_hybrid_recommendations(
            recommender=recommender,
            train_ratings=train_ratings,
            user_id=user_id,
            k=k
        )
    )

    hybrid_precision = precision_at_k(
        hybrid_recommendations,
        relevant_movies,
        k
    )

    hybrid_recall = recall_at_k(
        hybrid_recommendations,
        relevant_movies,
        k
    )

    hybrid_hit_rate = hit_rate_at_k(
        hybrid_recommendations,
        relevant_movies,
        k
    )

    return {
        "content_precision": content_precision,
        "content_recall": content_recall,
        "content_hit_rate": content_hit_rate,
        "hybrid_precision": hybrid_precision,
        "hybrid_recall": hybrid_recall,
        "hybrid_hit_rate": hybrid_hit_rate,
        "content_recommendations": content_recommendations,
        "hybrid_recommendations": hybrid_recommendations,
        "test_movie_id": test_movie_id
    }


# EVALUATE MODEL

def evaluate_model(
    recommender,
    ratings,
    k
):
    """
    Evaluate the recommendation model
    across multiple users.
    """

    random.seed(
        RANDOM_SEED
    )

    # FIND ELIGIBLE USERS

    eligible_users = []

    for user_id, user_ratings in (
        ratings.groupby("userId")
    ):

        if (
            len(user_ratings)
            < MIN_USER_RATINGS
        ):
            continue

        liked_movies = user_ratings[
            user_ratings["rating"] >= 4.0
        ]

        if liked_movies.empty:
            continue

        eligible_users.append(
            user_id
        )

    # Shuffle users for reproducibility
    random.shuffle(
        eligible_users
    )

    # Limit evaluation size
    eligible_users = eligible_users[
        :MAX_USERS
    ]

    print(
        f"\nUsers selected for evaluation: "
        f"{len(eligible_users)}"
    )

    # METRIC STORAGE

    content_precisions = []
    content_recalls = []
    content_hit_rates = []

    hybrid_precisions = []
    hybrid_recalls = []
    hybrid_hit_rates = []

    evaluated_users = 0

    # EVALUATE USERS

    for counter, user_id in enumerate(
        eligible_users,
        start=1
    ):

        result = evaluate_user(
            recommender=recommender,
            ratings=ratings,
            user_id=user_id,
            k=k
        )

        if result is None:
            continue

        content_precisions.append(
            result["content_precision"]
        )

        content_recalls.append(
            result["content_recall"]
        )

        content_hit_rates.append(
            result["content_hit_rate"]
        )

        hybrid_precisions.append(
            result["hybrid_precision"]
        )

        hybrid_recalls.append(
            result["hybrid_recall"]
        )

        hybrid_hit_rates.append(
            result["hybrid_hit_rate"]
        )

        evaluated_users += 1

        if counter % 10 == 0:

            print(
                f"Processed "
                f"{counter}/"
                f"{len(eligible_users)} users..."
            )

    # CALCULATE AVERAGES

    results = {

        "K": k,

        "Users Evaluated":
            evaluated_users,

        "Content-Based Precision@K":
            (
                sum(content_precisions)
                /
                len(content_precisions)
                if content_precisions
                else 0.0
            ),

        "Content-Based Recall@K":
            (
                sum(content_recalls)
                /
                len(content_recalls)
                if content_recalls
                else 0.0
            ),

        "Content-Based Hit Rate@K":
            (
                sum(content_hit_rates)
                /
                len(content_hit_rates)
                if content_hit_rates
                else 0.0
            ),

        "Hybrid Precision@K":
            (
                sum(hybrid_precisions)
                /
                len(hybrid_precisions)
                if hybrid_precisions
                else 0.0
            ),

        "Hybrid Recall@K":
            (
                sum(hybrid_recalls)
                /
                len(hybrid_recalls)
                if hybrid_recalls
                else 0.0
            ),

        "Hybrid Hit Rate@K":
            (
                sum(hybrid_hit_rates)
                /
                len(hybrid_hit_rates)
                if hybrid_hit_rates
                else 0.0
            )
    }

    return results


# PRINT RESULTS

def print_results(
    results
):
    """
    Print evaluation results.
    """

    print(
        "\n"
        + "=" * 70
    )

    print(
        "MODEL EVALUATION RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        f"K: {results['K']}"
    )

    print(
        f"Users Evaluated: "
        f"{results['Users Evaluated']}"
    )

    print(
        "\nCONTENT-BASED MODEL"
    )

    print(
        f"Precision@{results['K']}: "
        f"{results['Content-Based Precision@K']:.4f}"
    )

    print(
        f"Recall@{results['K']}: "
        f"{results['Content-Based Recall@K']:.4f}"
    )

    print(
        f"Hit Rate@{results['K']}: "
        f"{results['Content-Based Hit Rate@K']:.4f}"
    )

    print(
        "\nHYBRID MODEL"
    )

    print(
        f"Precision@{results['K']}: "
        f"{results['Hybrid Precision@K']:.4f}"
    )

    print(
        f"Recall@{results['K']}: "
        f"{results['Hybrid Recall@K']:.4f}"
    )

    print(
        f"Hit Rate@{results['K']}: "
        f"{results['Hybrid Hit Rate@K']:.4f}"
    )

    print(
        "=" * 70
    )


# MAIN

def main():

    print(
        "\n"
        + "=" * 70
    )

    print(
        "MOVIE RECOMMENDATION SYSTEM"
    )

    print(
        "AI MODEL EVALUATION"
    )

    print(
        "=" * 70
    )

    # LOAD RECOMMENDER

    print(
        "\nLoading recommendation engine..."
    )

    recommender = MovieRecommender(
        dataset_path=DATASET_PATH,
        ratings_path=RATINGS_PATH
    )

    # LOAD RATINGS

    print(
        "\nLoading ratings dataset..."
    )

    ratings = pd.read_csv(
        RATINGS_PATH
    )

    # NORMALIZE RATINGS

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

    ratings = ratings.dropna(
        subset=[
            "userId",
            "movieId",
            "rating"
        ]
    )

    ratings["userId"] = (
        ratings["userId"]
        .astype(int)
    )

    ratings["movieId"] = (
        ratings["movieId"]
        .astype(int)
    )

    print(
        f"Ratings loaded: "
        f"{len(ratings)}"
    )

    # RUN EVALUATION

    all_results = []

    for k in K_VALUES:

        print(
            "\n"
            + "-" * 70
        )

        print(
            f"Evaluating K = {k}"
        )

        print(
            "-" * 70
        )

        results = evaluate_model(
            recommender=recommender,
            ratings=ratings,
            k=k
        )

        all_results.append(
            results
        )

        print_results(
            results
        )

    # SAVE RESULTS

    results_df = pd.DataFrame(
        all_results
    )

    output_file = (
        "evaluation_results.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nResults saved to: "
        f"{output_file}"
    )

    # FINAL TABLE

    print(
        "\n"
        + "=" * 70
    )

    print(
        "FINAL COMPARISON"
    )

    print(
        "=" * 70
    )

    display_columns = [
        "K",
        "Content-Based Precision@K",
        "Content-Based Recall@K",
        "Content-Based Hit Rate@K",
        "Hybrid Precision@K",
        "Hybrid Recall@K",
        "Hybrid Hit Rate@K"
    ]

    print(
        results_df[
            display_columns
        ].to_string(
            index=False
        )
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "MODEL EVALUATION COMPLETED"
    )

    print(
        "=" * 70
    )


# RUN

if __name__ == "__main__":

    main()