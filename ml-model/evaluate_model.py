import pandas as pd

from recommender import MovieRecommender


def precision_at_k(
    recommended_movies,
    relevant_movies,
    k=10
):
    """
    Calculate Precision@K.

    recommended_movies:
        Movies recommended by the system.

    relevant_movies:
        Movies considered relevant/liked by the user.
    """

    recommended_movies = recommended_movies[:k]

    if len(recommended_movies) == 0:
        return 0.0

    recommended_ids = {
        movie["movieId"]
        for movie in recommended_movies
    }

    relevant_ids = set(relevant_movies)

    relevant_recommendations = (
        recommended_ids.intersection(relevant_ids)
    )

    precision = (
        len(relevant_recommendations)
        / len(recommended_movies)
    )

    return precision


def evaluate_movie_recommendations(
    recommender,
    ratings,
    user_id,
    movie_id,
    k=10
):

    # Movies rated by this user
    user_ratings = ratings[
        ratings["userId"] == user_id
    ]

    # Movies with rating >= 4 are treated as relevant
    liked_movies = user_ratings[
        user_ratings["rating"] >= 4
    ]["movieId"].tolist()

    # Find movie title
    movie_row = recommender.movies[
        recommender.movies["movieId"] == movie_id
    ]

    if movie_row.empty:
        return 0.0

    movie_title = movie_row.iloc[0]["title"]

    # Generate recommendations
    recommendations = recommender.recommend(
        movie_title,
        k
    )

    precision = precision_at_k(
        recommendations,
        liked_movies,
        k
    )

    return precision


if __name__ == "__main__":

    print("Loading recommendation model...")

    recommender = MovieRecommender()

    ratings = pd.read_csv(
        "dataset/ratings.csv"
    )

    # Example user/movie
    user_id = 1
    movie_id = 1

    precision = evaluate_movie_recommendations(
        recommender,
        ratings,
        user_id,
        movie_id,
        k=10
    )

    print("\n========== MODEL EVALUATION ==========")

    print(f"User ID: {user_id}")
    print(f"Movie ID: {movie_id}")
    print(f"Precision@10: {precision:.4f}")

    print("======================================")