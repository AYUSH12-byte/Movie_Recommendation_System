import os
import pickle
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:

    def __init__(self, dataset_path="dataset/movies.csv"):

        self.movies = pd.read_csv(dataset_path)

        self.movies["genres"] = self.movies["genres"].fillna("")
        self.movies["title"] = self.movies["title"].fillna("")

        self.movies["content"] = (
            self.movies["title"]
            + " "
            + self.movies["genres"]
        )

        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        self.movie_vectors = self.vectorizer.fit_transform(
            self.movies["content"]
        )

        self.movie_indices = pd.Series(
            self.movies.index,
            index=self.movies["title"]
        ).drop_duplicates()

    def recommend(
        self,
        movie_title,
        number_of_recommendations=10
    ):

        if movie_title not in self.movie_indices:
            return []

        movie_index = self.movie_indices[movie_title]

        similarity_scores = cosine_similarity(
            self.movie_vectors[movie_index],
            self.movie_vectors
        ).flatten()

        similar_indices = similarity_scores.argsort()[::-1]

        recommendations = []

        for index in similar_indices:

            if index == movie_index:
                continue

            recommendations.append({
                "movieId": int(
                    self.movies.iloc[index]["movieId"]
                ),
                "title": self.movies.iloc[index]["title"],
                "genres": self.movies.iloc[index]["genres"],
                "similarity_score": round(
                    float(similarity_scores[index]),
                    4
                )
            })

            if len(recommendations) >= number_of_recommendations:
                break

        return recommendations

    def recommend_for_user(
        self,
        user_id,
        ratings,
        number_of_recommendations=10
    ):

        user_ratings = ratings[
            ratings["userId"] == user_id
        ]

        if user_ratings.empty:
            return []

        liked_ratings = user_ratings[
            user_ratings["rating"] >= 4
        ]

        if liked_ratings.empty:
            return []

        recommendation_scores = {}

        for _, rating in liked_ratings.iterrows():

            movie_id = int(rating["movieId"])
            user_rating = float(rating["rating"])

            movie_row = self.movies[
                self.movies["movieId"] == movie_id
            ]

            if movie_row.empty:
                continue

            movie_title = movie_row.iloc[0]["title"]

            recommendations = self.recommend(
                movie_title,
                number_of_recommendations
            )

            for recommendation in recommendations:

                recommended_id = recommendation["movieId"]

                similarity = recommendation[
                    "similarity_score"
                ]

                weighted_score = (
                    similarity * user_rating
                )

                if recommended_id not in recommendation_scores:
                    recommendation_scores[
                        recommended_id
                    ] = 0

                recommendation_scores[
                    recommended_id
                ] += weighted_score

        rated_movie_ids = set(
            user_ratings["movieId"].astype(int)
        )

        recommendation_scores = {
            movie_id: score
            for movie_id, score
            in recommendation_scores.items()
            if movie_id not in rated_movie_ids
        }

        sorted_recommendations = sorted(
            recommendation_scores.items(),
            key=lambda item: item[1],
            reverse=True
        )

        results = []

        for movie_id, score in sorted_recommendations[
            :number_of_recommendations
        ]:

            movie_row = self.movies[
                self.movies["movieId"] == movie_id
            ]

            if movie_row.empty:
                continue

            movie = movie_row.iloc[0]

            results.append({
                "movieId": int(movie["movieId"]),
                "title": movie["title"],
                "genres": movie["genres"],
                "recommendation_score": round(
                    float(score),
                    4
                )
            })

        return results

    def save_model(
        self,
        model_path="models/movie_recommender.pkl"
    ):

        os.makedirs(
            os.path.dirname(model_path),
            exist_ok=True
        )

        model_data = {
            "movies": self.movies,
            "vectorizer": self.vectorizer,
            "movie_vectors": self.movie_vectors,
            "movie_indices": self.movie_indices,
        }

        with open(model_path, "wb") as file:
            pickle.dump(
                model_data,
                file
            )

        print(
            f"Model saved to: {model_path}"
        )


if __name__ == "__main__":

    print("Loading movie recommendation system...")

    recommender = MovieRecommender()

    print(
        f"Loaded {len(recommender.movies)} movies."
    )

    movie = "Toy Story (1995)"

    print(
        f"\nRecommendations for: {movie}\n"
    )

    recommendations = recommender.recommend(
        movie,
        10
    )

    for item in recommendations:

        print(
            f"{item['title']} "
            f"| {item['genres']} "
            f"| Score: {item['similarity_score']}"
        )

    ratings = pd.read_csv(
        "dataset/ratings.csv"
    )

    user_id = 1

    print(
        f"\nPersonalized recommendations "
        f"for User {user_id}:\n"
    )

    personalized = recommender.recommend_for_user(
        user_id,
        ratings,
        10
    )

    if personalized:

        for item in personalized:

            print(
                f"{item['title']} "
                f"| {item['genres']} "
                f"| Score: "
                f"{item['recommendation_score']}"
            )

    else:

        print(
            "Not enough rating history "
            "for personalized recommendations."
        )

    recommender.save_model()