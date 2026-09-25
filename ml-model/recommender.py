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

        print(
            "\n========================================"
        )

        print(
            "Initializing Movie Recommendation Engine"
        )

        print(
            "========================================"
        )

        # Load movies

        self.movies = pd.read_csv(
            dataset_path
        )

        # Clean movie data

        self.movies["movieId"] = pd.to_numeric(
            self.movies["movieId"],
            errors="coerce"
        )

        self.movies["title"] = (
            self.movies["title"]
            .fillna("")
            .astype(str)
        )

        self.movies["genres"] = (
            self.movies["genres"]
            .fillna("")
            .astype(str)
        )

        self.movies = self.movies.dropna(
            subset=["movieId"]
        )

        self.movies["movieId"] = (
            self.movies["movieId"]
            .astype(int)
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

        # Movie title index

        self.movie_indices = pd.Series(
            self.movies.index,
            index=self.movies["title"]
        ).drop_duplicates()

        # Load ratings

        self.ratings = pd.DataFrame()

        if os.path.exists(
            ratings_path
        ):

            try:

                self.ratings = pd.read_csv(
                    ratings_path
                )

                self.ratings["movieId"] = (
                    pd.to_numeric(
                        self.ratings["movieId"],
                        errors="coerce"
                    )
                )

                self.ratings["rating"] = (
                    pd.to_numeric(
                        self.ratings["rating"],
                        errors="coerce"
                    )
                )

                self.ratings = (
                    self.ratings.dropna(
                        subset=[
                            "movieId",
                            "rating"
                        ]
                    )
                )

                self.ratings["movieId"] = (
                    self.ratings["movieId"]
                    .astype(int)
                )

            except Exception as error:

                print(
                    "Warning: unable to load ratings."
                )

                print(error)

                self.ratings = pd.DataFrame()

        print(
            f"Movies loaded: {len(self.movies)}"
        )

        print(
            f"Ratings loaded: {len(self.ratings)}"
        )

        print(
            "Recommendation engine ready."
        )

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

    # GET MOVIE BY ID

    def get_movie_by_id(
        self,
        movie_id
    ):

        try:

            movie_id = int(
                movie_id
            )

        except (
            ValueError,
            TypeError
        ):

            return None

        movie_rows = self.movies[
            self.movies["movieId"]
            == movie_id
        ]

        if movie_rows.empty:

            return None

        movie = movie_rows.iloc[0]

        return {
            "movieId": int(
                movie["movieId"]
            ),

            "title": movie["title"],

            "genres": movie["genres"]
        }

    # GET MOVIE BY TITLE

    def get_movie_by_title(
        self,
        movie_title
    ):

        if movie_title not in self.movie_indices:

            return None

        movie_index = self.movie_indices[
            movie_title
        ]

        movie = self.movies.iloc[
            movie_index
        ]

        return {
            "movieId": int(
                movie["movieId"]
            ),

            "title": movie["title"],

            "genres": movie["genres"]
        }

    # CONTENT-BASED RECOMMENDATION

    def recommend(
        self,
        movie_title,
        number_of_recommendations=10
    ):

        if (
            number_of_recommendations
            < 1
        ):

            number_of_recommendations = 10

        if (
            number_of_recommendations
            > 100
        ):

            number_of_recommendations = 100

        # Check movie

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

        # Sort similarity scores

        similar_indices = (
            similarity_scores
            .argsort()[::-1]
        )

        recommendations = []

        for index in similar_indices:

            # Skip the original movie

            if index == movie_index:

                continue

            movie = self.movies.iloc[
                index
            ]

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

    # POPULARITY SCORE

    def calculate_popularity_scores(
        self,
        ratings
    ):

        if (
            ratings is None
            or
            ratings.empty
        ):

            return {}

        required_columns = [
            "movieId",
            "rating"
        ]

        for column in required_columns:

            if column not in ratings.columns:

                return {}

        data = ratings.copy()

        data["movieId"] = pd.to_numeric(
            data["movieId"],
            errors="coerce"
        )

        data["rating"] = pd.to_numeric(
            data["rating"],
            errors="coerce"
        )

        data = data.dropna(
            subset=[
                "movieId",
                "rating"
            ]
        )

        if data.empty:

            return {}

        # Movie statistics

        statistics = (
            data
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
        # Average Rating × log(Rating Count + 1)

        statistics[
            "popularity_score"
        ] = (

            statistics[
                "average_rating"
            ]

            *

            np.log1p(
                statistics[
                    "rating_count"
                ]
            )
        )

        max_score = statistics[
            "popularity_score"
        ].max()

        if max_score > 0:

            statistics[
                "popularity_normalized"
            ] = (

                statistics[
                    "popularity_score"
                ]

                /

                max_score
            )

        else:

            statistics[
                "popularity_normalized"
            ] = 0.0

        return dict(
            zip(
                statistics[
                    "movieId"
                ].astype(int),

                statistics[
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

        if (
            len(recommendations)
            <= number_of_recommendations
        ):

            return recommendations

        candidates = (
            recommendations.copy()
        )

        # Highest hybrid score first

        candidates.sort(
            key=lambda item:
                item.get(
                    "hybrid_score",
                    item.get(
                        "recommendation_score",
                        0
                    )
                ),
            reverse=True
        )

        selected = []

        # First recommendation

        first_movie = candidates.pop(
            0
        )

        first_movie[
            "diversity_score"
        ] = round(
            float(
                first_movie.get(
                    "hybrid_score",
                    0
                )
            ),
            4
        )

        selected.append(
            first_movie
        )

        # Select remaining recommendations

        while (
            candidates
            and
            len(selected)
            < number_of_recommendations
        ):

            best_candidate = None

            best_score = float(
                "-inf"
            )

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

                maximum_overlap = 0.0

                # Compare with selected movies

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
                        not candidate_genres
                        or
                        not selected_genres
                    ):

                        overlap = 0.0

                    else:

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

                        if union:

                            overlap = (
                                len(
                                    intersection
                                )
                                /
                                len(
                                    union
                                )
                            )

                        else:

                            overlap = 0.0

                    maximum_overlap = max(
                        maximum_overlap,
                        overlap
                    )

                # Apply diversity penalty

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

                if (
                    diversity_score
                    > best_score
                ):

                    best_score = (
                        diversity_score
                    )

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

    # PERSONALIZED HYBRID RECOMMENDATION

    def recommend_for_user(
        self,
        user_id,
        ratings,
        number_of_recommendations=10,
        minimum_rating=4.0
    ):

        if (
            ratings is None
            or
            ratings.empty
        ):

            return []

        required_columns = [
            "userId",
            "movieId",
            "rating"
        ]

        for column in required_columns:

            if column not in ratings.columns:

                return []

        data = ratings.copy()

        # Normalize types

        data["userId"] = (
            data["userId"]
            .astype(str)
        )

        data["movieId"] = pd.to_numeric(
            data["movieId"],
            errors="coerce"
        )

        data["rating"] = pd.to_numeric(
            data["rating"],
            errors="coerce"
        )

        data = data.dropna(
            subset=[
                "userId",
                "movieId",
                "rating"
            ]
        )

        user_id = str(
            user_id
        )

        # Current user's ratings

        user_ratings = data[
            data["userId"] == user_id
        ]

        if user_ratings.empty:

            return []

        # Movies user liked

        liked_ratings = (
            user_ratings[
                user_ratings["rating"]
                >= minimum_rating
            ]
            .sort_values(
                "rating",
                ascending=False
            )
        )

        if liked_ratings.empty:

            return []

        # Popularity

        popularity_scores = (
            self.calculate_popularity_scores(
                data
            )
        )

        recommendation_scores = {}

        # Generate candidates from liked movies

        for _, rating_row in (
            liked_ratings.iterrows()
        ):

            source_movie_id = int(
                rating_row["movieId"]
            )

            user_rating = float(
                rating_row["rating"]
            )

            source_movie = (
                self.get_movie_by_id(
                    source_movie_id
                )
            )

            if source_movie is None:

                continue

            source_movie_title = (
                source_movie["title"]
            )

            recommendations = (
                self.recommend(
                    movie_title=source_movie_title,
                    number_of_recommendations=(
                        number_of_recommendations
                        * 5
                    )
                )
            )

            for recommendation in (
                recommendations
            ):

                recommended_movie_id = int(
                    recommendation[
                        "movieId"
                    ]
                )

                similarity_score = float(
                    recommendation[
                        "similarity_score"
                    ]
                )

                # User preference score

                preference_score = (
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
                # Content similarity = 60%
                # User preference = 25%
                # Popularity = 15%

                hybrid_score = (
                    similarity_score
                    * 0.60
                    +
                    preference_score
                    * 0.25
                    +
                    popularity_score
                    * 0.15
                )

                # New candidate

                if (
                    recommended_movie_id
                    not in recommendation_scores
                ):

                    recommendation_scores[
                        recommended_movie_id
                    ] = {

                        "hybrid_score":
                            0.0,

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

                # Accumulate score

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

        # Remove movies user already rated

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

        # Create candidate list

        candidates = []

        for (
            movie_id,
            recommendation_data
        ) in recommendation_scores.items():

            movie = self.get_movie_by_id(
                movie_id
            )

            if movie is None:

                continue

            candidates.append({

                "movieId":
                    movie["movieId"],

                "title":
                    movie["title"],

                "genres":
                    movie["genres"],

                "similarity_score":
                    round(
                        float(
                            recommendation_data[
                                "similarity_score"
                            ]
                        ),
                        4
                    ),

                "popularity_score":
                    round(
                        float(
                            recommendation_data[
                                "popularity_score"
                            ]
                        ),
                        4
                    ),

                "recommendation_score":
                    round(
                        float(
                            recommendation_data[
                                "hybrid_score"
                            ]
                        ),
                        4
                    ),

                "hybrid_score":
                    float(
                        recommendation_data[
                            "hybrid_score"
                        ]
                    ),

                "sourceMovieId":
                    int(
                        recommendation_data[
                            "source_movie_id"
                        ]
                    ),

                "sourceMovieTitle":
                    recommendation_data[
                        "source_movie_title"
                    ],

                "sourceUserRating":
                    round(
                        float(
                            recommendation_data[
                                "source_user_rating"
                            ]
                        ),
                        1
                    )
            })

        # Diversity-aware reranking

        recommendations = (
            self.diversify_recommendations(
                recommendations=candidates,
                number_of_recommendations=(
                    number_of_recommendations
                ),
                diversity_weight=0.25
            )
        )

        # Remove internal field

        for item in recommendations:

            item.pop(
                "hybrid_score",
                None
            )

        return recommendations

    # COLD-START RECOMMENDATIONS

    def get_cold_start_recommendations(
        self,
        number_of_recommendations=10,
        minimum_ratings=10
    ):

        # Check ratings

        if self.ratings.empty:

            return []

        # Calculate statistics

        statistics = (
            self.ratings
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

        # Minimum rating threshold

        statistics = statistics[
            statistics[
                "totalRatings"
            ]
            >= minimum_ratings
        ]

        if statistics.empty:

            return []

        # Cold-start score
        # Average rating × log(rating count + 1)

        statistics[
            "coldStartScore"
        ] = (
            statistics[
                "averageRating"
            ]
            *
            np.log1p(
                statistics[
                    "totalRatings"
                ]
            )
        )

        # Sort candidates

        statistics = (
            statistics
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
            statistics.iterrows()
        ):

            movie_id = int(
                row["movieId"]
            )

            movie = self.get_movie_by_id(
                movie_id
            )

            if movie is None:

                continue

            candidates.append({

                "movieId":
                    movie["movieId"],

                "title":
                    movie["title"],

                "genres":
                    movie["genres"],

                "averageRating":
                    round(
                        float(
                            row[
                                "averageRating"
                            ]
                        ),
                        2
                    ),

                "totalRatings":
                    int(
                        row[
                            "totalRatings"
                        ]
                    ),

                "coldStartScore":
                    round(
                        float(
                            row[
                                "coldStartScore"
                            ]
                        ),
                        4
                    ),

                "recommendation_score":
                    round(
                        float(
                            row[
                                "coldStartScore"
                            ]
                        ),
                        4
                    )
            })

        # Diversity

        return self.diversify_cold_start(
            recommendations=candidates,
            number_of_recommendations=(
                number_of_recommendations
            )
        )

    # COLD-START DIVERSITY

    def diversify_cold_start(
        self,
        recommendations,
        number_of_recommendations
    ):

        if not recommendations:

            return []

        if (
            len(recommendations)
            <= number_of_recommendations
        ):

            return recommendations

        candidates = (
            recommendations.copy()
        )

        candidates.sort(
            key=lambda item:
                item["coldStartScore"],
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

            best_score = float(
                "-inf"
            )

            for candidate in candidates:

                candidate_genres = set(
                    self._get_genres(
                        candidate.get(
                            "genres",
                            ""
                        )
                    )
                )

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

                    if (
                        not candidate_genres
                        or
                        not selected_genres
                    ):

                        overlap = 0.0

                    else:

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

                        if union:

                            overlap = (
                                len(intersection)
                                /
                                len(union)
                            )

                        else:

                            overlap = 0.0

                    maximum_overlap = max(
                        maximum_overlap,
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
                            maximum_overlap
                        )
                    )
                )

                if (
                    diversity_score
                    > best_score
                ):

                    best_score = (
                        diversity_score
                    )

                    best_candidate = (
                        candidate
                    )

            if best_candidate is None:

                break

            best_candidate[
                "diversity_score"
            ] = round(
                float(
                    best_score
                ),
                4
            )

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
            f"\nModel saved to: {model_path}"
        )


# TESTING

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        "MOVIE RECOMMENDATION AI TEST"
    )

    print(
        "========================================"
    )

    # Initialize

    recommender = MovieRecommender()

    # Test 1: Content-based

    movie_title = "Toy Story (1995)"

    print(
        "\n1. CONTENT-BASED RECOMMENDATIONS"
    )

    print(
        f"Movie: {movie_title}"
    )

    print(
        "----------------------------------------"
    )

    content_results = recommender.recommend(
        movie_title=movie_title,
        number_of_recommendations=10
    )

    for index, item in enumerate(
        content_results,
        start=1
    ):

        print(
            f"{index}. "
            f"{item['title']} "
            f"| Similarity: "
            f"{item['similarity_score']} "
            f"| Genres: "
            f"{item['genres']}"
        )

    # Test 2: Personalized hybrid

    print(
        "\n2. PERSONALIZED HYBRID RECOMMENDATIONS"
    )

    print(
        "MovieLens User ID: 1"
    )

    print(
        "----------------------------------------"
    )

    if not recommender.ratings.empty:

        personalized_results = (
            recommender.recommend_for_user(
                user_id=1,
                ratings=recommender.ratings,
                number_of_recommendations=10
            )
        )

        if personalized_results:

            for index, item in enumerate(
                personalized_results,
                start=1
            ):

                print(
                    f"{index}. "
                    f"{item['title']} "
                    f"| Score: "
                    f"{item['recommendation_score']} "
                    f"| Similarity: "
                    f"{item['similarity_score']} "
                    f"| Popularity: "
                    f"{item['popularity_score']} "
                    f"| Genres: "
                    f"{item['genres']}"
                )

        else:

            print(
                "No personalized recommendations."
            )

    else:

        print(
            "Ratings dataset unavailable."
        )

    # Test 3: Cold start

    print(
        "\n3. COLD-START RECOMMENDATIONS"
    )

    print(
        "----------------------------------------"
    )

    cold_start_results = (
        recommender.get_cold_start_recommendations(
            number_of_recommendations=10
        )
    )

    if cold_start_results:

        for index, item in enumerate(
            cold_start_results,
            start=1
        ):

            print(
                f"{index}. "
                f"{item['title']} "
                f"| Average Rating: "
                f"{item['averageRating']} "
                f"| Ratings: "
                f"{item['totalRatings']} "
                f"| Score: "
                f"{item['coldStartScore']}"
            )

    else:

        print(
            "No cold-start recommendations."
        )

    # Save model

    print(
        "\n4. SAVING MODEL"
    )

    print(
        "----------------------------------------"
    )

    recommender.save_model()

    print(
        "\n========================================"
    )

    print(
        "ALL RECOMMENDATION TESTS COMPLETED"
    )

    print(
        "========================================"
    )