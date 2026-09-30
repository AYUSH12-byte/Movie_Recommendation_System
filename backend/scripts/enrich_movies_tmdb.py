import os
import sys
import time


# PROJECT ROOT

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


# IMPORT DATABASE

from app.database.database import (
    movies_collection
)

from app.services.tmdb_service import (
    search_tmdb_movie
)


# CONFIGURATION

BATCH_SIZE = 100

REQUEST_DELAY = 0.25


# TMDB FIELDS

TMDB_FIELDS = [
    "tmdbId",
    "posterUrl",
    "backdropUrl",
    "overview",
    "releaseDate",
    "tmdbRating",
    "tmdbVoteCount"
]


# ENRICH MOVIES

def enrich_movies():

    movies = movies_collection.find(
        {
            "tmdbId": {
                "$exists": False
            }
        },
        {
            "_id": 0,
            "movieId": 1,
            "title": 1
        }
    ).limit(
        BATCH_SIZE
    )

    movies = list(
        movies
    )

    total = len(
        movies
    )

    print(
        "=================================================="
    )

    print(
        "TMDB MOVIE ENRICHMENT"
    )

    print(
        "=================================================="
    )

    print(
        f"Movies selected: {total}"
    )

    print(
        f"Request delay: {REQUEST_DELAY} seconds"
    )

    print(
        "=================================================="
    )

    if not movies:

        print(
            "No movies need TMDB enrichment."
        )

        return

    success_count = 0

    failed_count = 0


    # PROCESS MOVIES

    for index, movie in enumerate(
        movies,
        start=1
    ):

        movie_id = movie.get(
            "movieId"
        )

        title = movie.get(
            "title",
            ""
        )

        print()

        print(
            f"[{index}/{total}] {title}"
        )

        if not title:

            print(
                "SKIPPED: Movie title is empty."
            )

            failed_count += 1

            continue


        # SEARCH TMDB

        tmdb_data = search_tmdb_movie(
            title
        )

        if not tmdb_data:

            print(
                "FAILED: TMDB movie not found."
            )

            failed_count += 1

            time.sleep(
                REQUEST_DELAY
            )

            continue


        # SAVE TO MONGODB

        update_data = {}

        for field in TMDB_FIELDS:

            value = tmdb_data.get(
                field
            )

            if value is not None:

                update_data[field] = value

        if not update_data:

            print(
                "FAILED: No TMDB metadata returned."
            )

            failed_count += 1

            time.sleep(
                REQUEST_DELAY
            )

            continue

        movies_collection.update_one(
            {
                "movieId": movie_id
            },
            {
                "$set": update_data
            }
        )


        # SUCCESS

        success_count += 1

        print(
            "SUCCESS:"
        )

        print(
            f"  TMDB ID: {tmdb_data.get('tmdbId')}"
        )

        print(
            f"  Poster: {tmdb_data.get('posterUrl')}"
        )

        print(
            f"  Release Date: {tmdb_data.get('releaseDate')}"
        )

        time.sleep(
            REQUEST_DELAY
        )


    # SUMMARY

    print()

    print(
        "=================================================="
    )

    print(
        "ENRICHMENT COMPLETE"
    )

    print(
        "=================================================="
    )

    print(
        f"Successful: {success_count}"
    )

    print(
        f"Failed: {failed_count}"
    )

    print(
        f"Total processed: {total}"
    )

    print(
        "=================================================="
    )


# MAIN

if __name__ == "__main__":

    enrich_movies()