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

        # Clean movie data

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

        # Create content features

        self.movies["content"] = (
            self.movies["title"]
            + " "
            + self.movies["genres"]
        )

        # TF-IDF

        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        self.movie_vectors = (
            self.vectorizer.fit_transform(
                self.movies["content"]
            )
        )

        # Movie index

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

        if number_of_recommendations < 1:
            number_of_recommendations = 10

        # Check movie

        if movie_title not in self.movie_indices:
            return []

        movie_index = self.movie_indices[
            movie_title
        ]

        # Cosine similarity

        similarity_scores = cosine_similarity(
            self.movie_vectors[movie_index],
            self.movie_vectors
        ).flatten()

        # Sort

        similar_indices = (
            similarity_scores
            .argsort()[::-1]
        )

        recommendations = []

        for index in similar_indices:

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

    # CALCULATE MOVIE POPULARITY

    def calculate_popularity_scores(
        self,
        ratings
    ):

        if ratings is None or ratings.empty:
            return {}

        required_columns = [
            "movieId",
            "rating"
        ]

        for column in required_columns:

            if column not in ratings.columns:
                return {}

        ratings = ratings.copy()

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
                "movieId",
                "rating"
            ]
        )

        if ratings.empty:
            return {}

        # Calculate average rating

        movie_statistics = (
            ratings
            .groupby("movieId")
            .agg(
                average_rating=(
                    "rating",
                    "mean"
                ),
                rating_count=(
                    "rating",
                    "count"
                )
            )
            .reset_index()
        )

        # Popularity formula
        #
        # average rating × log(rating count + 1)

        movie_statistics[
            "popularity_score"
        ] = (
            movie_statistics[
                "average_rating"
            ]
            *
            __import__("numpy").log1p(
                movie_statistics[
                    "rating_count"
                ]
            )
        )

        # Normalize popularity to 0-1

        max_score = (
            movie_statistics[
                "popularity_score"
            ].max()
        )

        if max_score > 0:

            movie_statistics[
                "popularity_normalized"
            ] = (
                movie_statistics[
                    "popularity_score"
                ]
                / max_score
            )

        else:

            movie_statistics[
                "popularity_normalized"
            ] = 0.0

        return dict(
            zip(
                movie_statistics[
                    "movieId"
                ].astype(int),
                movie_statistics[
                    "popularity_normalized"
                ]
            )
        )

    # PERSONALIZED HYBRID RECOMMENDATION

    def recommend_for_user(
        self,
        user_id,
        ratings,
        number_of_recommendations=10,
        minimum_rating=4.0
    ):

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

        # Copy ratings

        ratings = ratings.copy()

        # Normalize data types

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

        ratings = ratings.dropna(
            subset=[
                "userId",
                "movieId",
                "rating"
            ]
        )

        # Get current user's ratings

        user_id = str(user_id)

        user_ratings = ratings[
            ratings["userId"] == user_id
        ]

        if user_ratings.empty:
            return []

        # Get liked movies

        liked_ratings = user_ratings[
            user_ratings["rating"]
            >= minimum_rating
        ].sort_values(
            "rating",
            ascending=False
        )

        if liked_ratings.empty:
            return []

        # Popularity scores

        popularity_scores = (
            self.calculate_popularity_scores(
                ratings
            )
        )

        # Recommendation storage

        recommendation_scores = {}

        # Generate recommendations from liked movies

        for _, rating_row in liked_ratings.iterrows():

            source_movie_id = int(
                rating_row["movieId"]
            )

            user_rating = float(
                rating_row["rating"]
            )

            # Find source movie

            source_rows = self.movies[
                self.movies["movieId"]
                == source_movie_id
            ]

            if source_rows.empty:
                continue

            source_movie = (
                source_rows.iloc[0]
            )

            source_movie_title = (
                source_movie["title"]
            )

            # Get similar movies

            recommendations = self.recommend(
                movie_title=source_movie_title,
                number_of_recommendations=(
                    number_of_recommendations * 3
                )
            )

            # Process similar movies

            for recommendation in recommendations:

                recommended_movie_id = int(
                    recommendation["movieId"]
                )

                similarity_score = float(
                    recommendation[
                        "similarity_score"
                    ]
                )

                # Rating preference score
                #
                # Convert 0.5-5 rating into 0-1

                rating_preference_score = (
                    user_rating / 5.0
                )

                # Popularity score

                popularity_score = float(
                    popularity_scores.get(
                        recommended_movie_id,
                        0.0
                    )
                )

                # HYBRID SCORE
                #
                # Content       = 60%
                # User rating   = 25%
                # Popularity    = 15%

                hybrid_score = (
                    (
                        similarity_score
                        * 0.60
                    )
                    +
                    (
                        rating_preference_score
                        * 0.25
                    )
                    +
                    (
                        popularity_score
                        * 0.15
                    )
                )

                # Store recommendation

                if (
                    recommended_movie_id
                    not in recommendation_scores
                ):

                    recommendation_scores[
                        recommended_movie_id
                    ] = {
                        "hybrid_score": 0.0,
                        "similarity_score": (
                            similarity_score
                        ),
                        "popularity_score": (
                            popularity_score
                        ),
                        "source_movie_id": (
                            source_movie_id
                        ),
                        "source_movie_title": (
                            source_movie_title
                        ),
                        "source_user_rating": (
                            user_rating
                        )
                    }

                # Add score

                recommendation_scores[
                    recommended_movie_id
                ]["hybrid_score"] += (
                    hybrid_score
                )

                # Keep strongest source movie

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

                    recommendation_scores[
                        recommended_movie_id
                    ]["source_movie_id"] = (
                        source_movie_id
                    )

                    recommendation_scores[
                        recommended_movie_id
                    ]["source_movie_title"] = (
                        source_movie_title
                    )

                    recommendation_scores[
                        recommended_movie_id
                    ]["source_user_rating"] = (
                        user_rating
                    )

        # Remove already-rated movies

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

        # Sort by hybrid score

        sorted_recommendations = sorted(
            recommendation_scores.items(),
            key=lambda item: (
                item[1]["hybrid_score"]
            ),
            reverse=True
        )

        # Final results

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

                "popularity_score": round(
                    float(
                        recommendation_data[
                            "popularity_score"
                        ]
                    ),
                    4
                ),

                "recommendation_score": round(
                    float(
                        recommendation_data[
                            "hybrid_score"
                        ]
                    ),
                    4
                ),

                "sourceMovieId": int(
                    recommendation_data[
                        "source_movie_id"
                    ]
                ),

                "sourceMovieTitle": (
                    recommendation_data[
                        "source_movie_title"
                    ]
                ),

                "sourceUserRating": round(
                    float(
                        recommendation_data[
                            "source_user_rating"
                        ]
                    ),
                    1
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

        model_directory = os.path.dirname(
            model_path
        )

        if model_directory:

            os.makedirs(
                model_directory,
                exist_ok=True
            )

        model_data = {
            "movies": self.movies,
            "vectorizer": self.vectorizer,
            "movie_vectors": self.movie_vectors,
            "movie_indices": self.movie_indices
        }

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
        "\n========================================"
    )

    print(
        "HYBRID MOVIE RECOMMENDATION SYSTEM"
    )

    print(
        "========================================"
    )

    # Initialize

    recommender = MovieRecommender()

    # Content-based test

    movie = "Toy Story (1995)"

    print(
        f"\nContent-based recommendations "
        f"for: {movie}"
    )

    print(
        "----------------------------------------"
    )

    recommendations = recommender.recommend(
        movie_title=movie,
        number_of_recommendations=10
    )

    for index, item in enumerate(
        recommendations,
        start=1
    ):

        print(
            f"{index}. "
            f"{item['title']} "
            f"| Similarity: "
            f"{item['similarity_score']}"
        )

    # Load ratings

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

    # Personalized hybrid test

    user_id = 1

    print(
        f"\nHybrid personalized recommendations "
        f"for User {user_id}:"
    )

    print(
        "----------------------------------------"
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
                f"| Similarity: "
                f"{item['similarity_score']} "
                f"| Popularity: "
                f"{item['popularity_score']} "
                f"| Hybrid Score: "
                f"{item['recommendation_score']}"
            )

    else:

        print(
            "Not enough rating history "
            "for personalized recommendations."
        )

    # Save model

    recommender.save_model()

    print(
        "\n========================================"
    )

    print(
        "Hybrid recommendation test completed."
    )

    print(
        "========================================"
    )