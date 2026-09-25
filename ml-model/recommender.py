import os
import pickle

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:

    # INITIALIZE MODEL

    def __init__(
        self,
        dataset_path="dataset/movies.csv"
    ):

        self.movies = pd.read_csv(
            dataset_path
        )

        # Handle missing values

        self.movies["genres"] = (
            self.movies["genres"]
            .fillna("")
        )

        self.movies["title"] = (
            self.movies["title"]
            .fillna("")
        )

        # Create content field

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

        # Movie title -> dataframe index

        self.movie_indices = pd.Series(
            self.movies.index,
            index=self.movies["title"]
        ).drop_duplicates()

    # CONTENT-BASED RECOMMENDATION

    def recommend(
        self,
        movie_title,
        number_of_recommendations=10
    ):

        # Check movie exists

        if movie_title not in self.movie_indices:

            return []

        movie_index = self.movie_indices[
            movie_title
        ]

        # Calculate cosine similarity

        similarity_scores = cosine_similarity(
            self.movie_vectors[movie_index],
            self.movie_vectors
        ).flatten()

        # Sort by similarity

        similar_indices = (
            similarity_scores
            .argsort()[::-1]
        )

        recommendations = []

        # Build recommendations

        for index in similar_indices:

            # Skip original movie

            if index == movie_index:
                continue

            recommendations.append({

                "movieId": int(
                    self.movies.iloc[index][
                        "movieId"
                    ]
                ),

                "title": self.movies.iloc[index][
                    "title"
                ],

                "genres": self.movies.iloc[index][
                    "genres"
                ],

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

        # Validate ratings

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

        # Remove invalid data

        ratings = ratings.dropna(
            subset=[
                "userId",
                "movieId",
                "rating"
            ]
        )

        # Normalize current user ID

        user_id = str(user_id)

        # Get current user's ratings

        user_ratings = ratings[
            ratings["userId"] == user_id
        ]

        if user_ratings.empty:
            return []

        # Find highly rated movies

        liked_ratings = user_ratings[
            user_ratings["rating"]
            >= minimum_rating
        ].sort_values(
            "rating",
            ascending=False
        )

        if liked_ratings.empty:
            return []

        # Store recommendation scores

        recommendation_scores = {}

        # PROCESS EACH LIKED MOVIE

        for _, rating_row in (
            liked_ratings.iterrows()
        ):

            source_movie_id = int(
                rating_row["movieId"]
            )

            user_rating = float(
                rating_row["rating"]
            )

            # Find source movie

            movie_rows = self.movies[
                self.movies["movieId"]
                == source_movie_id
            ]

            if movie_rows.empty:
                continue

            source_movie = movie_rows.iloc[0]

            source_movie_title = (
                source_movie["title"]
            )

            # Get similar movies

            similar_movies = self.recommend(
                movie_title=source_movie_title,
                number_of_recommendations=(
                    number_of_recommendations
                )
            )

            # Process similar movies

            for recommendation in (
                similar_movies
            ):

                recommended_movie_id = int(
                    recommendation["movieId"]
                )

                similarity_score = float(
                    recommendation[
                        "similarity_score"
                    ]
                )

                # Weighted recommendation score
                #
                # High user rating
                #        ×
                # similarity
                #        =
                # recommendation strength

                weighted_score = (
                    similarity_score
                    * user_rating
                )

                # Create new recommendation

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
                ]["score"] += (
                    weighted_score
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

        # REMOVE ALREADY RATED MOVIES

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

            if movie_id
            not in rated_movie_ids
        }

        # SORT RECOMMENDATIONS

        sorted_recommendations = sorted(
            recommendation_scores.items(),
            key=lambda item: (
                item[1]["score"]
            ),
            reverse=True
        )

        # BUILD FINAL RESULTS

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


# TEST THE RECOMMENDER

if __name__ == "__main__":

    print(
        "Loading movie recommendation system..."
    )

    recommender = MovieRecommender()

    print(
        f"Loaded "
        f"{len(recommender.movies)} "
        f"movies."
    )

    # CONTENT-BASED TEST

    movie = "Toy Story (1995)"

    print(
        f"\nRecommendations for: "
        f"{movie}\n"
    )

    recommendations = (
        recommender.recommend(
            movie,
            10
        )
    )

    for item in recommendations:

        print(
            f"{item['title']} "
            f"| {item['genres']} "
            f"| Similarity: "
            f"{item['similarity_score']}"
        )

    # PERSONALIZED TEST

    ratings_path = (
        "dataset/ratings.csv"
    )

    if os.path.exists(
        ratings_path
    ):

        ratings = pd.read_csv(
            ratings_path
        )

        user_id = 1

        print(
            f"\nPersonalized recommendations "
            f"for User {user_id}:\n"
        )

        personalized = (
            recommender.recommend_for_user(
                user_id=user_id,
                ratings=ratings,
                number_of_recommendations=10
            )
        )

        if personalized:

            for item in personalized:

                print(
                    f"{item['title']} "
                    f"| {item['genres']} "
                    f"| Score: "
                    f"{item['recommendation_score']} "
                    f"| Based on: "
                    f"{item['sourceMovieTitle']} "
                    f"({item['sourceUserRating']}/5)"
                )

        else:

            print(
                "Not enough rating history "
                "for personalized recommendations."
            )

    else:

        print(
            "\nratings.csv not found."
        )

    # SAVE MODEL

    recommender.save_model()