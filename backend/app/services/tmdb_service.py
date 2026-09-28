import os
import re

import httpx
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


TMDB_API_KEY = os.getenv(
    "TMDB_API_KEY"
)

TMDB_BASE_URL = "https://api.themoviedb.org/3"

TMDB_IMAGE_BASE_URL = os.getenv(
    "TMDB_IMAGE_BASE_URL",
    "https://image.tmdb.org/t/p/w500"
)


# ============================================================
# CLEAN MOVIE TITLE
# ============================================================

def parse_movie_title(title: str):
    """
    Convert MovieLens title into:
    
    Example:
        Toy Story (1995)

    Returns:
        title = Toy Story
        year = 1995
    """

    if not title:
        return "", None

    title = str(title).strip()

    # Find year at the end of the title
    match = re.search(
        r"\((\d{4})\)\s*$",
        title
    )

    if match:

        year = int(
            match.group(1)
        )

        clean_title = re.sub(
            r"\s*\(\d{4}\)\s*$",
            "",
            title
        ).strip()

        return clean_title, year

    return title, None


# ============================================================
# SEARCH MOVIE ON TMDB
# ============================================================

def search_tmdb_movie(title: str):
    """
    Search TMDB using a MovieLens movie title.

    Handles MovieLens titles such as:

        Toy Story (1995)
        Jumanji (1995)
        Heat (1995)

    Returns:
        TMDB ID
        Poster URL
        Backdrop URL
        Overview
        Release date
        TMDB rating
        TMDB vote count
    """

    # --------------------------------------------------------
    # Validate API key
    # --------------------------------------------------------

    if not TMDB_API_KEY:

        print(
            "ERROR: TMDB_API_KEY is not configured."
        )

        return None

    if not title:

        print(
            "ERROR: Movie title is empty."
        )

        return None

    # --------------------------------------------------------
    # Parse MovieLens title
    # --------------------------------------------------------

    clean_title, year = parse_movie_title(
        title
    )

    print(
        f"TMDB SEARCH: '{clean_title}'"
    )

    if year:
        print(
            f"TMDB YEAR: {year}"
        )

    # --------------------------------------------------------
    # Prepare TMDB request
    # --------------------------------------------------------

    params = {
        "api_key": TMDB_API_KEY,
        "query": clean_title,
        "include_adult": False,
        "language": "en-US",
    }

    # Only send year when available
    if year:
        params["year"] = year

    # --------------------------------------------------------
    # Call TMDB
    # --------------------------------------------------------

    try:

        response = httpx.get(
            f"{TMDB_BASE_URL}/search/movie",
            params=params,
            timeout=10,
        )

        print(
            "TMDB STATUS:",
            response.status_code
        )

        # ----------------------------------------------------
        # API error
        # ----------------------------------------------------

        if response.status_code != 200:

            print(
                "TMDB ERROR:",
                response.text
            )

            return None

        # ----------------------------------------------------
        # Parse response
        # ----------------------------------------------------

        data = response.json()

        results = data.get(
            "results",
            []
        )

        print(
            "TMDB RESULTS:",
            len(results)
        )

        if not results:

            # ------------------------------------------------
            # Fallback search without year
            # ------------------------------------------------

            print(
                "TMDB: Retrying without year..."
            )

            fallback_params = {
                "api_key": TMDB_API_KEY,
                "query": clean_title,
                "include_adult": False,
                "language": "en-US",
            }

            fallback_response = httpx.get(
                f"{TMDB_BASE_URL}/search/movie",
                params=fallback_params,
                timeout=10,
            )

            print(
                "TMDB FALLBACK STATUS:",
                fallback_response.status_code
            )

            if fallback_response.status_code != 200:

                print(
                    "TMDB FALLBACK ERROR:",
                    fallback_response.text
                )

                return None

            fallback_data = (
                fallback_response.json()
            )

            results = fallback_data.get(
                "results",
                []
            )

            print(
                "TMDB FALLBACK RESULTS:",
                len(results)
            )

            if not results:

                print(
                    f"TMDB: No movie found for '{title}'"
                )

                return None

        # ----------------------------------------------------
        # Select best result
        # ----------------------------------------------------

        movie = results[0]

        poster_path = movie.get(
            "poster_path"
        )

        backdrop_path = movie.get(
            "backdrop_path"
        )

        # ----------------------------------------------------
        # Build metadata
        # ----------------------------------------------------

        movie_data = {

            "tmdbId": movie.get(
                "id"
            ),

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

        print(
            "TMDB MOVIE:",
            movie_data
        )

        return movie_data

    # --------------------------------------------------------
    # Request error
    # --------------------------------------------------------

    except httpx.RequestError as error:

        print(
            "TMDB REQUEST ERROR:",
            error
        )

        return None

    # --------------------------------------------------------
    # Unexpected error
    # --------------------------------------------------------

    except Exception as error:

        print(
            "TMDB UNEXPECTED ERROR:",
            error
        )

        return None