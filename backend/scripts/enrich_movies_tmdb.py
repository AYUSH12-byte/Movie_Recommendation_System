import argparse
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

from app.database.database import movies_collection
from app.services.tmdb_service import search_tmdb_movie


# CONFIGURATION

DEFAULT_LIMIT = 100
DEFAULT_DELAY = 0.25


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


# ARGUMENTS

def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Enrich MongoDB movies with TMDB metadata."
        )
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=(
            "Number of movies to process. "
            "Default: 100"
        )
    )

    parser.add_argument(
        "--skip",
        type=int,
        default=0,
        help=(
            "Number of unenriched movies to skip. "
            "Default: 0"
        )
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=(
            "Delay between TMDB requests in seconds. "
            "Default: 0.25"
        )
    )

    return parser.parse_args()


# ENRICH MOVIES

def enrich_movies(
    limit,
    skip,
    delay
):

    query = {
        "tmdbId": {
            "$exists": False
        }
    }

    movies = movies_collection.find(
        query,
        {
            "_id": 0,
            "movieId": 1,
            "title": 1
        }
    ).sort(
        "movieId",
        1
    ).skip(
        skip
    ).limit(
        limit
    )

    movies = list(
        movies
    )

    total = len(
        movies
    )

    print()
    print("=" * 60)
    print("TMDB MOVIE ENRICHMENT")
    print("=" * 60)
    print(f"Selected movies : {total}")
    print(f"Skip            : {skip}")
    print(f"Delay           : {delay}s")
    print("=" * 60)

    if not movies:

        print()
        print(
            "No unenriched movies found."
        )
        print()

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
            f"[{index}/{total}] "
            f"Movie ID: {movie_id}"
        )

        print(
            f"Title: {title}"
        )


        # EMPTY TITLE

        if not title:

            print(
                "SKIPPED: Empty movie title."
            )

            failed_count += 1

            continue


        # TMDB SEARCH

        try:

            tmdb_data = search_tmdb_movie(
                title
            )

        except Exception as error:

            print(
                f"ERROR: {error}"
            )

            failed_count += 1

            time.sleep(
                delay
            )

            continue


        # TMDB NOT FOUND

        if not tmdb_data:

            print(
                "NOT FOUND: TMDB returned no result."
            )

            failed_count += 1

            time.sleep(
                delay
            )

            continue


        # PREPARE DATA

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
                delay
            )

            continue


        # SAVE TO MONGODB

        movies_collection.update_one(
            {
                "movieId": movie_id
            },
            {
                "$set": update_data
            }
        )

        success_count += 1


        # SUCCESS OUTPUT

        print(
            "SUCCESS"
        )

        print(
            f"TMDB ID: "
            f"{tmdb_data.get('tmdbId')}"
        )

        print(
            f"Poster: "
            f"{tmdb_data.get('posterUrl')}"
        )

        print(
            f"Release: "
            f"{tmdb_data.get('releaseDate')}"
        )


        # REQUEST DELAY

        time.sleep(
            delay
        )


    # SUMMARY

    print()
    print("=" * 60)
    print("ENRICHMENT COMPLETE")
    print("=" * 60)

    print(
        f"Successful : {success_count}"
    )

    print(
        f"Failed     : {failed_count}"
    )

    print(
        f"Processed  : {total}"
    )

    print("=" * 60)
    print()


# MAIN

if __name__ == "__main__":

    args = parse_arguments()

    if args.limit < 1:

        print(
            "ERROR: --limit must be at least 1."
        )

        sys.exit(1)

    if args.skip < 0:

        print(
            "ERROR: --skip cannot be negative."
        )

        sys.exit(1)

    if args.delay < 0:

        print(
            "ERROR: --delay cannot be negative."
        )

        sys.exit(1)

    enrich_movies(
        limit=args.limit,
        skip=args.skip,
        delay=args.delay
    )