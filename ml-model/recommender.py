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

        # Combine movie title and genres
        self.movies["content"] = (
            self.movies["title"]
            + " "
            + self.movies["genres"]
        )

        # TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        self.movie_vectors = self.vectorizer.fit_transform(
            self.movies["content"]
        )

        # Movie title -> index
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

        # Calculate similarity ONLY for selected movie
        similarity_scores = cosine_similarity(
            self.movie_vectors[movie_index],
            self.movie_vectors
        ).flatten()

        # Get movie indexes sorted by similarity
        similar_indices = similarity_scores.argsort()[::-1]

        recommendations = []

        for index in similar_indices:

            # Skip the selected movie
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
            pickle.dump(model_data, file)

        print(f"Model saved to: {model_path}")


if __name__ == "__main__":

    recommender = MovieRecommender()

    print(
        f"Loaded {len(recommender.movies)} movies."
    )

    movie = "Toy Story (1995)"

    recommendations = recommender.recommend(
        movie,
        10
    )

    print(
        f"\nRecommendations for: {movie}\n"
    )

    for item in recommendations:
        print(
            f"{item['title']} "
            f"| {item['genres']} "
            f"| Score: {item['similarity_score']}"
        )

    recommender.save_model()