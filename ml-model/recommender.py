import os
import pickle

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:

    # ============================================================
    # INITIALIZATION
    # ============================================================

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

        # ========================================================
        # LOAD MOVIES
        # ========================================================

        self.movies = pd.read_csv(
            dataset_path
        )

        # ========================================================
        # CLEAN MOVIE DATA
        # ========================================================

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

        # ========================================================
        # RESET INDEX
        # ========================================================

        self.movies = self.movies.reset_index(
            drop=True
        )

        # ========================================================
        # CREATE CONTENT FIELD
        # ========================================================

        self.movies["content"] = (
            self.movies["title"]
            + " "
            + self.movies["genres"]
        )

        # ========================================================
        # TF-IDF VECTORIZER
        # ========================================================

        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        self.movie_vectors = (
            self.vectorizer.fit_transform(
                self.movies["content"]
            )
        )

        # ========================================================
        # MOVIE TITLE INDEX
        # ========================================================
        #
        # IMPORTANT:
        # Use a dictionary instead of a Pandas Series.
        #
        # This prevents:
        #
        # ValueError:
        # The truth value of a Series is ambiguous.
        #
        # ========================================================

        self.movie_indices = {}

        for index, title in (
            self.movies["title"].items()
        ):

            if title not in self.movie_indices:

                self.movie_indices[
                    title
                ] = index

        # ========================================================
        # LOAD RATINGS
        # ========================================================

        self.ratings = pd.DataFrame()

        if os.path.exists(
            ratings_path
        ):

            try:

                self.ratings = pd.read_csv(
                    ratings_path
                )

                # Convert movie IDs

                self.ratings["movieId"] = (
                    pd.to_numeric(
                        self.ratings["movieId"],
                        errors="coerce"
                    )
                )

                # Convert ratings

                self.ratings["rating"] = (
                    pd.to_numeric(
                        self.ratings["rating"],
                        errors="coerce"
                    )
                )

                # Remove invalid rows

                self.ratings = (
                    self.ratings.dropna(
                        subset=[
                            "movieId",
                            "rating"
                        ]
                    )
                )

                # Convert movie ID to integer

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

        # ========================================================
        # INITIALIZATION INFORMATION
        # ========================================================

        print(
            f"Movies loaded: "
            f"{len(self.movies)}"
        )

        print(
            f"Ratings loaded: "
            f"{len(self.ratings)}"
        )

        print(
            "Recommendation engine ready."
        )

    # ============================================================
    # GENRE HELPER
    # ============================================================

    @staticmethod
    def _get_genres(
        genres
    ):

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

    # ============================================================
    # GET MOVIE BY ID
    # ============================================================

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

    # ============================================================
    # GET MOVIE BY TITLE
    # ============================================================

    def get_movie_by_title(
        self,
        movie_title
    ):

        if not movie_title:

            return None

        movie_title = str(
            movie_title
        ).strip()

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

    # ============================================================
    # CONTENT-BASED RECOMMENDATION
    # ============================================================

    def recommend(
        self,
        movie_title,
        number_of_recommendations=10
    ):

        # ========================================================
        # VALIDATE LIMIT
        # ========================================================

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

        # ========================================================
        # CLEAN TITLE
        # ========================================================

        if not movie_title:

            return []

        movie_title = str(
            movie_title
        ).strip()

        # ========================================================
        # CHECK MOVIE
        # ========================================================

        if movie_title not in self.movie_indices:

            return []

        # ========================================================
        # GET MOVIE INDEX
        # ========================================================

        movie_index = self.movie_indices[
            movie_title
        ]

        # ========================================================
        # COSINE SIMILARITY
        # ========================================================

        similarity_scores = cosine_similarity(
            self.movie_vectors[movie_index],
            self.movie_vectors
        ).flatten()

        # ========================================================
        # SORT SIMILAR MOVIES
        # ========================================================

        similar_indices = (
            similarity_scores
            .argsort()[::-1]
        )

        recommendations = []

        # ========================================================
        # CREATE RECOMMENDATIONS
        # ========================================================

        for index in similar_indices:

            # Convert NumPy integer to Python integer

            index = int(
                index
            )

            # ----------------------------------------------------
            # SKIP ORIGINAL MOVIE
            # ----------------------------------------------------

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

            # ----------------------------------------------------
            # STOP WHEN ENOUGH MOVIES FOUND
            # ----------------------------------------------------

            if (
                len(recommendations)
                >= number_of_recommendations
            ):

                break

        return recommendations

    # ============================================================
    # POPULARITY SCORE
    # ============================================================

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

        # ========================================================
        # NORMALIZE TYPES
        # ========================================================

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

        # ========================================================
        # MOVIE STATISTICS
        # ========================================================

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

        # ========================================================
        # POPULARITY FORMULA
        #
        # Average Rating × log(Rating Count + 1)
        # ========================================================

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

        # ========================================================
        # NORMALIZE POPULARITY
        # ========================================================

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

        # ========================================================
        # RETURN DICTIONARY
        # ========================================================

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

    # ============================================================
    # DIVERSITY-AWARE RERANKING
    # ============================================================

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

        # ========================================================
        # SORT BY HYBRID SCORE
        # ========================================================

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

        # ========================================================
        # FIRST MOVIE
        # ========================================================

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

        # ========================================================
        # SELECT REMAINING MOVIES
        # ========================================================

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

                # ------------------------------------------------
                # COMPARE WITH SELECTED MOVIES
                # ------------------------------------------------

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

                # ------------------------------------------------
                # APPLY DIVERSITY PENALTY
                # ------------------------------------------------

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

    # ============================================================
    # PERSONALIZED HYBRID RECOMMENDATION
    # ============================================================

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

        # ========================================================
        # NORMALIZE TYPES
        # ========================================================

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

        # ========================================================
        # CURRENT USER RATINGS
        # ========================================================

        user_ratings = data[
            data["userId"] == user_id
        ]

        if user_ratings.empty:

            return []

        # ========================================================
        # MOVIES USER LIKED
        # ========================================================

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

        # ========================================================
        # POPULARITY
        # ========================================================

        popularity_scores = (
            self.calculate_popularity_scores(
                data
            )
        )

        recommendation_scores = {}

        # ========================================================
        # GENERATE CANDIDATES
        # ========================================================

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

                # =================================================
                # USER PREFERENCE SCORE
                # =================================================

                preference_score = (
                    user_rating / 5.0
                )

                # =================================================
                # POPULARITY SCORE
                # =================================================

                popularity_score = float(
                    popularity_scores.get(
                        recommended_movie_id,
                        0.0
                    )
                )

                # =================================================
                # HYBRID SCORE
                #
                # Content Similarity = 60%
                # User Preference    = 25%
                # Popularity         = 15%
                # =================================================

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

                # =================================================
                # CREATE NEW CANDIDATE
                # =================================================

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

                # =================================================
                # ACCUMULATE SCORE
                # =================================================

                recommendation_scores[
                    recommended_movie_id
                ]["hybrid_score"] += (
                    hybrid_score
                )

                # =================================================
                # KEEP STRONGEST SOURCE MOVIE
                # =================================================

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

        # ========================================================
        # REMOVE MOVIES ALREADY RATED
        # ========================================================

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

        # ========================================================
        # CREATE CANDIDATE LIST
        # ========================================================

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

        # ========================================================
        # DIVERSITY-AWARE RERANKING
        # ========================================================

        recommendations = (
            self.diversify_recommendations(
                recommendations=candidates,
                number_of_recommendations=(
                    number_of_recommendations
                ),
                diversity_weight=0.25
            )
        )

        # ========================================================
        # REMOVE INTERNAL FIELD
        # ========================================================

        for item in recommendations:

            item.pop(
                "hybrid_score",
                None
            )

        return recommendations

    # ============================================================
    # COLD-START RECOMMENDATIONS
    # ============================================================

    def get_cold_start_recommendations(
        self,
        number_of_recommendations=10,
        minimum_ratings=10
    ):

        # ========================================================
        # CHECK RATINGS
        # ========================================================

        if self.ratings.empty:

            return []

        # ========================================================
        # CALCULATE MOVIE STATISTICS
        # ========================================================

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

        # ========================================================
        # MINIMUM RATING THRESHOLD
        # ========================================================

        statistics = statistics[
            statistics[
                "totalRatings"
            ]
            >= minimum_ratings
        ]

        if statistics.empty:

            return []

        # ========================================================
        # COLD-START SCORE
        #
        # Average Rating × log(Rating Count + 1)
        # ========================================================

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

        # ========================================================
        # SORT CANDIDATES
        # ========================================================

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

        # ========================================================
        # CREATE CANDIDATES
        # ========================================================

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

        # ========================================================
        # DIVERSITY
        # ========================================================

        return self.diversify_cold_start(
            recommendations=candidates,
            number_of_recommendations=(
                number_of_recommendations
            )
        )

    # ============================================================
    # COLD-START DIVERSITY
    # ============================================================

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

        # ========================================================
        # SELECT DIVERSE MOVIES
        # ========================================================

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

                # =================================================
                # DIVERSITY PENALTY
                # =================================================

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

    # ============================================================
    # SAVE MODEL
    # ============================================================

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


# ============================================================
# TESTING
# ============================================================

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

    # ========================================================
    # INITIALIZE
    # ========================================================

    recommender = MovieRecommender()

    # ========================================================
    # TEST 1: CONTENT-BASED
    # ========================================================

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

    # ========================================================
    # TEST 2: PERSONALIZED HYBRID
    # ========================================================

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

    # ========================================================
    # TEST 3: COLD START
    # ========================================================

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

    # ========================================================
    # TEST 4: SAVE MODEL
    # ========================================================

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