import os
import random

import pandas as pd
import matplotlib.pyplot as plt

from recommender import MovieRecommender


# CONFIGURATION

DATASET_PATH = "dataset/movies.csv"
RATINGS_PATH = "dataset/ratings.csv"

K_VALUES = [5, 10, 20]

MIN_USER_RATINGS = 5

MAX_USERS = 100

RANDOM_SEED = 42

OUTPUT_CSV = "evaluation_results.csv"
OUTPUT_CHART = "evaluation_results.png"


# CONTENT-BASED USER RECOMMENDATIONS

def get_content_based_recommendations(
    recommender,
    train_ratings,
    user_id,
    number_of_recommendations
):
    """
    Generate content-based recommendations
    using the movies liked by the user.
    """

    user_ratings = train_ratings[
        train_ratings["userId"] == user_id
    ]

    liked_movies = user_ratings[
        user_ratings["rating"] >= 4.0
    ]

    if liked_movies.empty:
        return []

    recommendation_scores = {}

    rated_movie_ids = set(
        user_ratings["movieId"].astype(int)
    )

    for _, rating in liked_movies.iterrows():

        movie_id = int(
            rating["movieId"]
        )

        movie = recommender.get_movie_by_id(
            movie_id
        )

        if movie is None:
            continue

        movie_title = movie["title"]

        recommendations = recommender.recommend(
            movie_title=movie_title,
            number_of_recommendations=(
                number_of_recommendations * 5
            )
        )

        for recommendation in recommendations:

            recommended_movie_id = int(
                recommendation["movieId"]
            )

            if recommended_movie_id in rated_movie_ids:
                continue

            similarity_score = float(
                recommendation.get(
                    "similarity_score",
                    0
                )
            )

            current_score = recommendation_scores.get(
                recommended_movie_id,
                0
            )

            recommendation_scores[
                recommended_movie_id
            ] = max(
                current_score,
                similarity_score
            )

    sorted_recommendations = sorted(
        recommendation_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return [
        movie_id
        for movie_id, _ in sorted_recommendations[
            :number_of_recommendations
        ]
    ]


# HYBRID USER RECOMMENDATIONS

def get_hybrid_recommendations(
    recommender,
    train_ratings,
    user_id,
    number_of_recommendations
):
    """
    Generate recommendations using the
    hybrid recommendation engine.
    """

    recommendations = (
        recommender.recommend_for_user(
            user_id=str(user_id),
            ratings=train_ratings,
            number_of_recommendations=(
                number_of_recommendations
            )
        )
    )

    return [
        int(recommendation["movieId"])
        for recommendation in recommendations
    ]


# METRIC CALCULATION

def calculate_metrics(
    recommended_movie_ids,
    relevant_movie_ids,
    k
):
    """
    Calculate Precision@K, Recall@K
    and Hit Rate@K.
    """

    recommended_set = set(
        recommended_movie_ids[:k]
    )

    relevant_set = set(
        relevant_movie_ids
    )

    hits = len(
        recommended_set.intersection(
            relevant_set
        )
    )

    precision = (
        hits / k
        if k > 0
        else 0
    )

    recall = (
        hits / len(relevant_set)
        if len(relevant_set) > 0
        else 0
    )

    hit_rate = (
        1
        if hits > 0
        else 0
    )

    return {
        "precision": precision,
        "recall": recall,
        "hit_rate": hit_rate,
        "hits": hits
    }


# EVALUATE MODEL

def evaluate_model(
    recommender,
    ratings,
    k,
    max_users=MAX_USERS
):
    """
    Evaluate content-based and hybrid
    recommendation approaches.
    """

    random.seed(
        RANDOM_SEED
    )

    ratings = ratings.copy()

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

    eligible_users = []

    for user_id, user_ratings in ratings.groupby(
        "userId"
    ):

        if len(user_ratings) < MIN_USER_RATINGS:
            continue

        liked_ratings = user_ratings[
            user_ratings["rating"] >= 4.0
        ]

        if liked_ratings.empty:
            continue

        eligible_users.append(
            user_id
        )

    random.shuffle(
        eligible_users
    )

    eligible_users = eligible_users[
        :max_users
    ]

    print(
        f"\nEvaluating {len(eligible_users)} users..."
    )

    content_precisions = []
    content_recalls = []
    content_hit_rates = []

    hybrid_precisions = []
    hybrid_recalls = []
    hybrid_hit_rates = []

    content_recommendation_ids = set()
    hybrid_recommendation_ids = set()

    evaluated_users = 0

    for index, user_id in enumerate(
        eligible_users,
        start=1
    ):

        user_ratings = ratings[
            ratings["userId"] == user_id
        ].copy()

        liked_ratings = user_ratings[
            user_ratings["rating"] >= 4.0
        ]

        if liked_ratings.empty:
            continue

        # HOLD OUT ONE LIKED MOVIE

        test_rating = liked_ratings.sample(
            n=1,
            random_state=RANDOM_SEED
        )

        test_movie_id = int(
            test_rating.iloc[0]["movieId"]
        )

        relevant_movie_ids = [
            test_movie_id
        ]

        train_ratings = user_ratings[
            user_ratings["movieId"]
            != test_movie_id
        ].copy()

        # CONTENT-BASED

        content_recommendations = (
            get_content_based_recommendations(
                recommender=recommender,
                train_ratings=train_ratings,
                user_id=user_id,
                number_of_recommendations=k
            )
        )

        content_metrics = calculate_metrics(
            recommended_movie_ids=(
                content_recommendations
            ),
            relevant_movie_ids=(
                relevant_movie_ids
            ),
            k=k
        )

        content_precisions.append(
            content_metrics["precision"]
        )

        content_recalls.append(
            content_metrics["recall"]
        )

        content_hit_rates.append(
            content_metrics["hit_rate"]
        )

        content_recommendation_ids.update(
            content_recommendations
        )

        # HYBRID

        hybrid_recommendations = (
            get_hybrid_recommendations(
                recommender=recommender,
                train_ratings=train_ratings,
                user_id=user_id,
                number_of_recommendations=k
            )
        )

        hybrid_metrics = calculate_metrics(
            recommended_movie_ids=(
                hybrid_recommendations
            ),
            relevant_movie_ids=(
                relevant_movie_ids
            ),
            k=k
        )

        hybrid_precisions.append(
            hybrid_metrics["precision"]
        )

        hybrid_recalls.append(
            hybrid_metrics["recall"]
        )

        hybrid_hit_rates.append(
            hybrid_metrics["hit_rate"]
        )

        hybrid_recommendation_ids.update(
            hybrid_recommendations
        )

        evaluated_users += 1

        if index % 10 == 0:

            print(
                f"Processed {index}/"
                f"{len(eligible_users)} users..."
            )

    # COVERAGE

    total_movies = len(
        recommender.movies
    )

    content_coverage = (
        len(content_recommendation_ids)
        / total_movies
        if total_movies > 0
        else 0
    )

    hybrid_coverage = (
        len(hybrid_recommendation_ids)
        / total_movies
        if total_movies > 0
        else 0
    )

    # FINAL RESULTS

    results = {
        "K": k,

        "Users Evaluated": evaluated_users,

        "Content-Based Precision@K": (
            sum(content_precisions)
            / len(content_precisions)
            if content_precisions
            else 0
        ),

        "Content-Based Recall@K": (
            sum(content_recalls)
            / len(content_recalls)
            if content_recalls
            else 0
        ),

        "Content-Based Hit Rate@K": (
            sum(content_hit_rates)
            / len(content_hit_rates)
            if content_hit_rates
            else 0
        ),

        "Content-Based Coverage": (
            content_coverage
        ),

        "Hybrid Precision@K": (
            sum(hybrid_precisions)
            / len(hybrid_precisions)
            if hybrid_precisions
            else 0
        ),

        "Hybrid Recall@K": (
            sum(hybrid_recalls)
            / len(hybrid_recalls)
            if hybrid_recalls
            else 0
        ),

        "Hybrid Hit Rate@K": (
            sum(hybrid_hit_rates)
            / len(hybrid_hit_rates)
            if hybrid_hit_rates
            else 0
        ),

        "Hybrid Coverage": (
            hybrid_coverage
        )
    }

    return results


# DISPLAY RESULTS

def display_results(results_df):

    print(
        "\n"
        + "=" * 80
    )

    print(
        "MODEL EVALUATION RESULTS"
    )

    print(
        "=" * 80
    )

    for _, row in results_df.iterrows():

        print(
            f"\nK = {int(row['K'])}"
        )

        print(
            f"Users Evaluated: "
            f"{int(row['Users Evaluated'])}"
        )

        print(
            "\nContent-Based:"
        )

        print(
            f"  Precision@K: "
            f"{row['Content-Based Precision@K']:.4f}"
        )

        print(
            f"  Recall@K: "
            f"{row['Content-Based Recall@K']:.4f}"
        )

        print(
            f"  Hit Rate@K: "
            f"{row['Content-Based Hit Rate@K']:.4f}"
        )

        print(
            f"  Coverage: "
            f"{row['Content-Based Coverage']:.4f}"
        )

        print(
            "\nHybrid:"
        )

        print(
            f"  Precision@K: "
            f"{row['Hybrid Precision@K']:.4f}"
        )

        print(
            f"  Recall@K: "
            f"{row['Hybrid Recall@K']:.4f}"
        )

        print(
            f"  Hit Rate@K: "
            f"{row['Hybrid Hit Rate@K']:.4f}"
        )

        print(
            f"  Coverage: "
            f"{row['Hybrid Coverage']:.4f}"
        )


# CREATE COMPARISON CHART

def create_comparison_chart(
    results_df
):

    metrics = [
        "Precision@K",
        "Recall@K",
        "Hit Rate@K"
    ]

    for metric in metrics:

        plt.figure(
            figsize=(8, 5)
        )

        x = range(
            len(results_df)
        )

        width = 0.35

        content_values = []

        hybrid_values = []

        for _, row in results_df.iterrows():

            if metric == "Precision@K":

                content_values.append(
                    row[
                        "Content-Based Precision@K"
                    ]
                )

                hybrid_values.append(
                    row[
                        "Hybrid Precision@K"
                    ]
                )

            elif metric == "Recall@K":

                content_values.append(
                    row[
                        "Content-Based Recall@K"
                    ]
                )

                hybrid_values.append(
                    row[
                        "Hybrid Recall@K"
                    ]
                )

            else:

                content_values.append(
                    row[
                        "Content-Based Hit Rate@K"
                    ]
                )

                hybrid_values.append(
                    row[
                        "Hybrid Hit Rate@K"
                    ]
                )

        content_positions = [
            value - width / 2
            for value in x
        ]

        hybrid_positions = [
            value + width / 2
            for value in x
        ]

        plt.bar(
            content_positions,
            content_values,
            width,
            label="Content-Based"
        )

        plt.bar(
            hybrid_positions,
            hybrid_values,
            width,
            label="Hybrid"
        )

        plt.xticks(
            list(x),
            [
                f"K={int(k)}"
                for k in results_df["K"]
            ]
        )

        plt.ylabel(
            metric
        )

        plt.xlabel(
            "Recommendation List Size"
        )

        plt.title(
            f"Content-Based vs Hybrid - {metric}"
        )

        plt.legend()

        plt.tight_layout()

        chart_path = (
            f"evaluation_{metric.lower().replace('@', '_at_').replace(' ', '_')}.png"
        )

        plt.savefig(
            chart_path,
            dpi=300
        )

        plt.close()

        print(
            f"Chart saved: {chart_path}"
        )


# MAIN

def main():

    print(
        "\n"
        + "=" * 80
    )

    print(
        "MOVIE RECOMMENDATION SYSTEM"
    )

    print(
        "AI MODEL EVALUATION"
    )

    print(
        "=" * 80
    )

    print(
        "\nLoading recommendation engine..."
    )

    recommender = MovieRecommender(
        dataset_path=DATASET_PATH,
        ratings_path=RATINGS_PATH
    )

    print(
        "\nLoading ratings..."
    )

    ratings = pd.read_csv(
        RATINGS_PATH
    )

    print(
        f"Ratings loaded: {len(ratings)}"
    )

    all_results = []

    for k in K_VALUES:

        print(
            "\n"
            + "-" * 80
        )

        print(
            f"Evaluating K={k}"
        )

        print(
            "-" * 80
        )

        result = evaluate_model(
            recommender=recommender,
            ratings=ratings,
            k=k
        )

        all_results.append(
            result
        )

    results_df = pd.DataFrame(
        all_results
    )

    # SAVE RESULTS

    results_df.to_csv(
        OUTPUT_CSV,
        index=False
    )

    print(
        f"\nEvaluation results saved to: "
        f"{OUTPUT_CSV}"
    )

    # DISPLAY

    display_results(
        results_df
    )

    # CHARTS

    create_comparison_chart(
        results_df
    )

    print(
        "\n"
        + "=" * 80
    )

    print(
        "MODEL EVALUATION COMPLETED"
    )

    print(
        "=" * 80
    )


if __name__ == "__main__":
    main()