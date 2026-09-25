import os
import pickle

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:

    # INITIALIZATION

    def __init__(
        self,
        dataset_path="dataset/movies.csv",
        ratings_path="dataset/ratings.csv"
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

        # Load MovieLens ratings for cold-start

        self.ratings = pd.DataFrame()

        if os.path.exists(ratings_path):

            try:

                self.ratings = pd.read_csv(
                    ratings_path
                )

                print(
                    f"Loaded {len(self.ratings)} "
                    f"ratings for popularity analysis."
                )

            except Exception as error:

                print(
                    "Could not load ratings dataset:"
                )

                print(error)

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

        # Calculate average rating and rating count

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

            np.log1p(
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

                /

                max_score
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

    # DIVERSITY-AWARE RERANKING

    def diversify_recommendations(
        self,
        recommendations,
        number_of_recommendations=10,
        diversity_weight=0.25
    ):

        if not recommendations:

            return []

        if len(recommendations) <= number_of_recommendations:

            return recommendations

        candidates = recommendations.copy()

        selected = []

        # Select first movie using highest recommendation score

        candidates.sort(
            key=lambda item: (
                item.get(
                    "hybrid_score",
                    item.get(
                        "recommendation_score",
                        0
                    )
                )
            ),
            reverse=True
        )

        first_movie = candidates.pop(0)

        selected.append(
            first_movie
        )

        # Select remaining movies

        while (
            candidates
            and
            len(selected)
            < number_of_recommendations
        ):

            best_candidate = None
            best_score = float("-inf")

            for candidate in candidates:

                base_score = float(
                    candidate.get(
                        "hybrid_score",
                        candidate.get(
                            "recommendation_score",
                            0
                        )
                    )
                )

                candidate_genres = set(
                    self._get_genres(
                        candidate.get(
                            "genres",
                            ""
                        )
                    )
                )

                # Calculate maximum genre overlap

                maximum_overlap = 0.0

                for selected_movie in selected:

                    selected_genres = set(
                        self._get_genres(
                            selected_movie.get(
                                "genres",
                                ""
                            )
                        )
                    )

                    if not candidate_genres:

                        overlap = 0.0

                    elif not selected_genres:

                        overlap = 0.0

                    else:

                        intersection = (
                            candidate_genres
                            & selected_genres
                        )

                        union = (
                            candidate_genres
                            | selected_genres
                        )

                        overlap = (
                            len(intersection)
                            /
                            len(union)
                        )

                    maximum_overlap = max(
                        maximum_overlap,
                        overlap
                    )

                # Diversity penalty

                diversity_score = (
                    base_score
                    *
                    (
                        1
                        -
                        (
                            diversity_weight
                            *
                            maximum_overlap
                        )
                    )
                )

                if diversity_score > best_score:

                    best_score = diversity_score
                    best_candidate = candidate

            if best_candidate is None:

                break

            best_candidate[
                "diversity_score"
            ] = round(
                float(best_score),
                4
            )

            selected.append(
                best_candidate
            )

            candidates.remove(
                best_candidate
            )

        return selected

    # GENRE HELPER

    @staticmethod
    def _get_genres(genres):

        if not genres:

            return []

        genres = str(
            genres
        )

        if genres == "(no genres listed)":

            return []

        return [
            genre.strip()
            for genre in genres.split("|")
            if genre.strip()
        ]

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

        user_id = str(
            user_id
        )

        # Get current user's ratings

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

        recommendation_scores = {}

        # Generate recommendations

        for _, rating_row in (
            liked_ratings.iterrows()
        ):

            source_movie_id = int(
                rating_row["movieId"]
            )

            user_rating = float(
                rating_row["rating"]
            )

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

            recommendations = self.recommend(
                movie_title=source_movie_title,
                number_of_recommendations=(
                    number_of_recommendations * 5
                )
            )

            for recommendation in recommendations:

                recommended_movie_id = int(
                    recommendation["movieId"]
                )

                similarity_score = float(
                    recommendation[
                        "similarity_score"
                    ]
                )

                rating_preference_score = (
                    user_rating / 5.0
                )

                popularity_score = float(
                    popularity_scores.get(
                        recommended_movie_id,
                        0.0
                    )
                )

                # Hybrid score
                #
                # Content      = 60%
                # Preference   = 25%
                # Popularity   = 15%

                hybrid_score = (

                    similarity_score
                    * 0.60

                    +

                    rating_preference_score
                    * 0.25

                    +

                    popularity_score
                    * 0.15
                )

                if (
                    recommended_movie_id
                    not in recommendation_scores
                ):

                    recommendation_scores[
                        recommended_movie_id
                    ] = {

                        "hybrid_score": 0.0,

                        "similarity_score":
                            similarity_score,

                        "popularity_score":
                            popularity_score,

                        "source_movie_id":
                            source_movie_id,

                        "source_movie_title":
                            source_movie_title,

                        "source_user_rating":
                            user_rating
                    }

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

            if movie_id
            not in rated_movie_ids
        }

        if not recommendation_scores:

            return []

        # Convert to candidate list

        candidates = []

        for (
            movie_id,
            recommendation_data
        ) in recommendation_scores.items():

            movie_rows = self.movies[
                self.movies["movieId"]
                == movie_id
            ]

            if movie_rows.empty:

                continue

            movie = movie_rows.iloc[0]

            candidates.append({

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

                "hybrid_score": float(
                    recommendation_data[
                        "hybrid_score"
                    ]
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

        # Diversity-aware reranking

        diverse_results = (
            self.diversify_recommendations(
                recommendations=candidates,
                number_of_recommendations=(
                    number_of_recommendations
                ),
                diversity_weight=0.25
            )
        )

        # Remove internal scoring field

        for item in diverse_results:

            item.pop(
                "hybrid_score",
                None
            )

        return diverse_results

    # COLD-START RECOMMENDATIONS

    def get_cold_start_recommendations(
        self,
        number_of_recommendations=10
    ):

        if self.ratings.empty:

            return []

        required_columns = [
            "movieId",
            "rating"
        ]

        for column in required_columns:

            if column not in self.ratings.columns:

                return []

        ratings = self.ratings.copy()

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

            return []

        # Calculate movie statistics

        movie_statistics = (
            ratings
            .groupby("movieId")
            .agg(
                averageRating=(
                    "rating",
                    "mean"
                ),
                totalRatings=(
                    "rating",
                    "count"
                )
            )
            .reset_index()
        )

        # Minimum rating count
        #
        # Avoid recommending movies with only
        # one or two ratings.

        movie_statistics = (
            movie_statistics[
                movie_statistics[
                    "totalRatings"
                ] >= 10
            ]
        )

        if movie_statistics.empty:

            return []

        # Popularity formula

        movie_statistics[
            "coldStartScore"
        ] = (

            movie_statistics[
                "averageRating"
            ]

            *

            np.log1p(
                movie_statistics[
                    "totalRatings"
                ]
            )
        )

        # Sort

        movie_statistics = (
            movie_statistics
            .sort_values(
                "coldStartScore",
                ascending=False
            )
            .head(
                number_of_recommendations * 5
            )
        )

        candidates = []

        for _, row in (
            movie_statistics.iterrows()
        ):

            movie_id = int(
                row["movieId"]
            )

            movie_rows = self.movies[
                self.movies["movieId"]
                == movie_id
            ]

            if movie_rows.empty:

                continue

            movie = movie_rows.iloc[0]

            candidates.append({

                "movieId": movie_id,

                "title": movie["title"],

                "genres": movie["genres"],

                "averageRating": round(
                    float(
                        row["averageRating"]
                    ),
                    2
                ),

                "totalRatings": int(
                    row["totalRatings"]
                ),

                "coldStartScore": round(
                    float(
                        row["coldStartScore"]
                    ),
                    4
                ),

                "recommendation_score": round(
                    float(
                        row["coldStartScore"]
                    ),
                    4
                )
            })

        # Apply diversity

        diversified = (
            self.diversify_cold_start(
                candidates,
                number_of_recommendations
            )
        )

        return diversified

    # COLD-START DIVERSITY

    def diversify_cold_start(
        self,
        recommendations,
        number_of_recommendations
    ):

        if not recommendations:

            return []

        if len(recommendations) <= number_of_recommendations:

            return recommendations

        candidates = recommendations.copy()

        candidates.sort(
            key=lambda item: item[
                "coldStartScore"
            ],
            reverse=True
        )

        selected = [
            candidates.pop(0)
        ]

        while (
            candidates
            and
            len(selected)
            < number_of_recommendations
        ):

            best_candidate = None
            best_score = float("-inf")

            for candidate in candidates:

                candidate_genres = set(
                    self._get_genres(
                        candidate.get(
                            "genres",
                            ""
                        )
                    )
                )

                max_overlap = 0.0

                for selected_movie in selected:

                    selected_genres = set(
                        self._get_genres(
                            selected_movie.get(
                                "genres",
                                ""
                            )
                        )
                    )

                    if (
                        candidate_genres
                        and
                        selected_genres
                    ):

                        intersection = (
                            candidate_genres
                            &
                            selected_genres
                        )

                        union = (
                            candidate_genres
                            |
                            selected_genres
                        )

                        overlap = (
                            len(intersection)
                            /
                            len(union)
                        )

                        max_overlap = max(
                            max_overlap,
                            overlap
                        )

                diversity_score = (
                    candidate[
                        "coldStartScore"
                    ]
                    *
                    (
                        1
                        -
                        (
                            0.25
                            *
                            max_overlap
                        )
                    )
                )

                if (
                    diversity_score
                    >
                    best_score
                ):

                    best_score = (
                        diversity_score
                    )

                    best_candidate = candidate

            if best_candidate is None:

                break

            selected.append(
                best_candidate
            )

            candidates.remove(
                best_candidate
            )

        return selected

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

            "movies":
                self.movies,

            "vectorizer":
                self.vectorizer,

            "movie_vectors":
                self.movie_vectors,

            "movie_indices":
                self.movie_indices
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

    # Hybrid test

    if not recommender.ratings.empty:

        print(
            "\nHybrid personalized recommendations "
            "for MovieLens User 1:"
        )

        print(
            "----------------------------------------"
        )

        personalized = (
            recommender.recommend_for_user(
                user_id=1,
                ratings=recommender.ratings,
                number_of_recommendations=10
            )
        )

        for index, item in enumerate(
            personalized,
            start=1
        ):

            print(
                f"{index}. "
                f"{item['title']} "
                f"| Score: "
                f"{item['recommendation_score']} "
                f"| Genres: "
                f"{item['genres']}"
            )

    # Cold-start test

    print(
        "\nCold-start recommendations:"
    )

    print(
        "----------------------------------------"
    )

    cold_start = (
        recommender.get_cold_start_recommendations(
            number_of_recommendations=10
        )
    )

    for index, item in enumerate(
        cold_start,
        start=1
    ):

        print(
            f"{index}. "
            f"{item['title']} "
            f"| Rating: "
            f"{item['averageRating']} "
            f"| Ratings: "
            f"{item['totalRatings']} "
            f"| Score: "
            f"{item['coldStartScore']}"
        )

    # Save model

    recommender.save_model()

    print(
        "\n========================================"
    )

    print(
        "Recommendation tests completed."
    )

    print(
        "========================================"
    )