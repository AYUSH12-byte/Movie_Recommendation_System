import os
import pickle

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:

    # INITIALIZATION

    def __init__(
        self,
        dataset_path="dataset/movies.csv"
    ):

        print("Loading movie dataset...")

        self.movies = pd.read_csv(
            dataset_path
        )

        # Clean missing values

        self.movies["genres"] = (
            self.movies["genres"]
            .fillna("")
            .astype(str)
        )

        self.movies["title"] = (
            self.movies["title"]
            .fillna("")
            .astype(str)
        )

        # Create content column

        self.movies["content"] = (
            self.movies["title"]
            + " "
            + self.movies["genres"]
        )

        # TF-IDF Vectorizer

        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        self.movie_vectors = (
            self.vectorizer.fit_transform(
                self.movies["content"]
            )
        )

        # Movie title -> DataFrame index

        self.movie_indices = pd.Series(
            self.movies.index,
            index=self.movies["title"]
        ).drop_duplicates()

        print(
            f"Loaded {len(self.movies)} movies."
        )

    # CONTENT-BASED RECOMMENDATION

    def recommend(
        self,
        movie_title,
        number_of_recommendations=10
    ):

        # Validate recommendation count

        if number_of_recommendations < 1:
            number_of_recommendations = 10

        # Check movie existence

        if movie_title not in self.movie_indices:
            return []

        # Get selected movie index

        movie_index = self.movie_indices[
            movie_title
        ]

        # Calculate cosine similarity

        similarity_scores = cosine_similarity(
            self.movie_vectors[movie_index],
            self.movie_vectors
        ).flatten()

        # Sort movies by similarity

        similar_indices = (
            similarity_scores
            .argsort()[::-1]
        )

        recommendations = []

        # Build recommendation list

        for index in similar_indices:

            # Don't recommend the same movie

            if index == movie_index:
                continue

            movie = self.movies.iloc[index]

            recommendations.append({
                "movieId": int(
                    movie["movieId"]
                ),
                "title": movie["title"],
                "genres": movie["genres"],
                "similarity_score": round(
                    float(
                        similarity_scores[index]
                    ),
                    4
                )
            })

            if (
                len(recommendations)
                >= number_of_recommendations
            ):
                break

        return recommendations

    # PERSONALIZED RECOMMENDATION

    def recommend_for_user(
        self,
        user_id,
        ratings,
        number_of_recommendations=10,
        minimum_rating=4.0
    ):

        # Validate ratings DataFrame

        if ratings is None:
            return []

        if ratings.empty:
            return []

        required_columns = [
            "userId",
            "movieId",
            "rating"
        ]

        for column in required_columns:

            if column not in ratings.columns:
                return []

        # Normalize user ID
        #
        # MongoDB userId is stored as string.
        # MovieLens userId is normally integer.
        # Converting both to string allows both formats.

        ratings = ratings.copy()

        ratings["userId"] = (
            ratings["userId"]
            .astype(str)
        )

        ratings["movieId"] = pd.to_numeric(
            ratings["movieId"],
            errors="coerce"
        )

        ratings["rating"] = pd.to_numeric(
            ratings["rating"],
            errors="coerce"
        )

        # Remove invalid rating records

        ratings = ratings.dropna(
            subset=[
                "userId",
                "movieId",
                "rating"
            ]
        )

        # Get ratings for current user

        user_id = str(user_id)

        user_ratings = ratings[
            ratings["userId"] == user_id
        ]

        if user_ratings.empty:
            return []

        # Get movies liked by the user
        #
        # Default:
        # rating >= 4.0 means the user liked the movie.

        liked_ratings = user_ratings[
            user_ratings["rating"]
            >= minimum_rating
        ]

        if liked_ratings.empty:
            return []

        # Dictionary used to combine recommendation scores
        #
        # Example:
        #
        # Movie A similarity from Movie X = 0.8
        # User rating for Movie X = 5
        #
        # Weighted score = 0.8 * 5 = 4.0

        recommendation_scores = {}

        # Generate recommendations from every liked movie

        for _, rating_row in liked_ratings.iterrows():

            movie_id = int(
                rating_row["movieId"]
            )

            user_rating = float(
                rating_row["rating"]
            )

            # Find movie in MovieLens dataset

            movie_rows = self.movies[
                self.movies["movieId"]
                == movie_id
            ]

            if movie_rows.empty:
                continue

            movie_title = (
                movie_rows.iloc[0]["title"]
            )

            # Get similar movies

            recommendations = self.recommend(
                movie_title=movie_title,
                number_of_recommendations=(
                    number_of_recommendations
                )
            )

            # Calculate weighted recommendation scores

            for recommendation in recommendations:

                recommended_movie_id = int(
                    recommendation["movieId"]
                )

                similarity_score = float(
                    recommendation[
                        "similarity_score"
                    ]
                )

                weighted_score = (
                    similarity_score
                    * user_rating
                )

                if (
                    recommended_movie_id
                    not in recommendation_scores
                ):
                    recommendation_scores[
                        recommended_movie_id
                    ] = {
                        "score": 0.0,
                        "similarity_score": (
                            similarity_score
                        )
                    }

                recommendation_scores[
                    recommended_movie_id
                ]["score"] += weighted_score

                # Keep the highest similarity score

                if (
                    similarity_score
                    >
                    recommendation_scores[
                        recommended_movie_id
                    ]["similarity_score"]
                ):
                    recommendation_scores[
                        recommended_movie_id
                    ]["similarity_score"] = (
                        similarity_score
                    )

        # Remove movies already rated by the user

        rated_movie_ids = set(
            user_ratings[
                "movieId"
            ]
            .astype(int)
            .tolist()
        )

        recommendation_scores = {
            movie_id: data
            for movie_id, data
            in recommendation_scores.items()
            if movie_id not in rated_movie_ids
        }

        # Sort by recommendation score

        sorted_recommendations = sorted(
            recommendation_scores.items(),
            key=lambda item: (
                item[1]["score"]
            ),
            reverse=True
        )

        # Build final result

        results = []

        for (
            movie_id,
            recommendation_data
        ) in sorted_recommendations:

            movie_rows = self.movies[
                self.movies["movieId"]
                == movie_id
            ]

            if movie_rows.empty:
                continue

            movie = movie_rows.iloc[0]

            results.append({
                "movieId": int(
                    movie["movieId"]
                ),
                "title": movie["title"],
                "genres": movie["genres"],
                "similarity_score": round(
                    float(
                        recommendation_data[
                            "similarity_score"
                        ]
                    ),
                    4
                ),
                "recommendation_score": round(
                    float(
                        recommendation_data[
                            "score"
                        ]
                    ),
                    4
                )
            })

            if (
                len(results)
                >= number_of_recommendations
            ):
                break

        return results

    # SAVE MODEL

    def save_model(
        self,
        model_path="models/movie_recommender.pkl"
    ):

        # Create model directory

        model_directory = os.path.dirname(
            model_path
        )

        if model_directory:
            os.makedirs(
                model_directory,
                exist_ok=True
            )

        # Data to save

        model_data = {
            "movies": self.movies,
            "vectorizer": self.vectorizer,
            "movie_vectors": self.movie_vectors,
            "movie_indices": self.movie_indices
        }

        # Save using pickle

        with open(
            model_path,
            "wb"
        ) as file:

            pickle.dump(
                model_data,
                file
            )

        print(
            f"Model saved to: {model_path}"
        )


# TESTING

if __name__ == "__main__":

    print(
        "\nMOVIE RECOMMENDATION SYSTEM"
    )

    # Initialize recommender

    recommender = MovieRecommender()

    # Test content-based recommendation

    movie = "Toy Story (1995)"

    print(
        f"\nRecommendations for: {movie}"
    )

    recommendations = recommender.recommend(
        movie_title=movie,
        number_of_recommendations=10
    )

    if recommendations:

        for index, item in enumerate(
            recommendations,
            start=1
        ):

            print(
                f"{index}. "
                f"{item['title']} "
                f"| {item['genres']} "
                f"| Similarity: "
                f"{item['similarity_score']}"
            )

    else:

        print(
            "No recommendations found."
        )

    # Load MovieLens ratings

    print(
        "\nLoading ratings dataset..."
    )

    try:

        ratings = pd.read_csv(
            "dataset/ratings.csv"
        )

        print(
            f"Loaded {len(ratings)} ratings."
        )

    except FileNotFoundError:

        print(
            "ratings.csv not found."
        )

        ratings = pd.DataFrame()

    # Test personalized recommendation

    user_id = 1

    print(
        f"\nPersonalized recommendations "
        f"for User {user_id}:"
    )

    personalized = (
        recommender.recommend_for_user(
            user_id=user_id,
            ratings=ratings,
            number_of_recommendations=10
        )
    )

    if personalized:

        for index, item in enumerate(
            personalized,
            start=1
        ):

            print(
                f"{index}. "
                f"{item['title']} "
                f"| {item['genres']} "
                f"| Similarity: "
                f"{item['similarity_score']} "
                f"| Recommendation Score: "
                f"{item['recommendation_score']}"
            )

    else:

        print(
            "Not enough rating history "
            "for personalized recommendations."
        )

    # Save trained model

    print(
        "\nSaving recommendation model..."
    )

    recommender.save_model()

    print(
        "\nRecommendation system test completed."
    )