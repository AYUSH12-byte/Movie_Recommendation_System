import sys
import os

# ==========================================
# ADD ML-MODEL PATH
# ==========================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../ml-model"
    )
)

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


from recommender import MovieRecommender


# ==========================================
# CREATE RECOMMENDER INSTANCE
# ==========================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "movies.csv"
)

recommender = MovieRecommender(
    MODEL_PATH
)


# ==========================================
# GET MOVIE RECOMMENDATIONS
# ==========================================

def get_movie_recommendations(
    movie_title: str,
    limit: int = 10
):

    recommendations = recommender.recommend(
        movie_title,
        limit
    )

    return recommendations