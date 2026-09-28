import os

import httpx
from dotenv import load_dotenv


load_dotenv()


TMDB_API_KEY = os.getenv("TMDB_API_KEY")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = os.getenv(
    "TMDB_IMAGE_BASE_URL",
    "https://image.tmdb.org/t/p/w500"
)


def search_tmdb_movie(title: str):
    """
    Search TMDB using a movie title and return
    useful metadata for the frontend.
    """

    if not TMDB_API_KEY:
        print("TMDB_API_KEY is not configured.")
        return None

    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "include_adult": False,
        "language": "en-US",
    }

    try:
        response = httpx.get(
            f"{TMDB_BASE_URL}/search/movie",
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get(
            "results",
            []
        )

        if not results:
            return None

        movie = results[0]

        poster_path = movie.get(
            "poster_path"
        )

        backdrop_path = movie.get(
            "backdrop_path"
        )

        return {
            "tmdbId": movie.get("id"),

            "overview": movie.get(
                "overview",
                ""
            ),

            "releaseDate": movie.get(
                "release_date",
                ""
            ),

            "posterUrl": (
                f"{TMDB_IMAGE_BASE_URL}{poster_path}"
                if poster_path
                else None
            ),

            "backdropUrl": (
                f"{TMDB_IMAGE_BASE_URL}{backdrop_path}"
                if backdrop_path
                else None
            ),

            "tmdbRating": movie.get(
                "vote_average"
            ),

            "tmdbVoteCount": movie.get(
                "vote_count"
            ),
        }

    except Exception as error:

        print(
            f"TMDB search failed for '{title}': {error}"
        )

        return None