import os
import sys

import pandas as pd
from pymongo import UpdateOne


# ADD BACKEND TO PYTHON PATH

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


from app.database.database import (
    movies_collection
)

# DATASET PATH

DATASET_PATH = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        "ml-model",
        "dataset",
        "movies.csv"
    )
)


# IMPORT MOVIES
def import_movies():

    print("Loading MovieLens dataset...")

    movies = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"Found {len(movies)} movies."
    )

    operations = []

    for _, movie in movies.iterrows():

        movie_id = int(
            movie["movieId"]
        )

        title = str(
            movie["title"]
        )

        genres = str(
            movie["genres"]
        )

        operations.append(
            UpdateOne(
                {
                    "movieId": movie_id
                },
                {
                    "$set": {
                        "movieId": movie_id,
                        "title": title,
                        "genres": genres
                    },
                    "$setOnInsert": {
                        "averageRating": 0.0,
                        "totalRatings": 0
                    }
                },
                upsert=True
            )
        )

    if operations:

        result = movies_collection.bulk_write(
            operations
        )

        print(
            f"Inserted: {result.upserted_count}"
        )

        print(
            f"Updated: {result.modified_count}"
        )

    print(
        "Movie import completed successfully."
    )


if __name__ == "__main__":

    import_movies()