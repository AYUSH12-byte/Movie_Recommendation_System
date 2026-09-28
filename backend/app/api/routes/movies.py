from fastapi import (
    APIRouter,
    HTTPException,
    Query
)

from app.database.database import (
    movies_collection
)

from app.services.movie_service import (
    get_popular_movies,
    get_trending_movies,
    enrich_movie_with_tmdb
)


router = APIRouter(
    prefix="/api/movies",
    tags=["Movies"]
)


# GET POPULAR MOVIES

@router.get("/popular")
def popular_movies(
    limit: int = Query(
        10,
        ge=1,
        le=50
    ),
    minimum_ratings: int = Query(
        3,
        ge=1,
        le=100
    )
):

    movies = get_popular_movies(
        limit=limit,
        minimum_ratings=minimum_ratings
    )

    return {
        "success": True,
        "type": "popular",
        "count": len(movies),
        "movies": movies
    }


# GET TRENDING MOVIES

@router.get("/trending")
def trending_movies(
    limit: int = Query(
        10,
        ge=1,
        le=50
    ),
    days: int = Query(
        30,
        ge=1,
        le=365
    )
):

    movies = get_trending_movies(
        limit=limit,
        days=days
    )

    return {
        "success": True,
        "type": "trending",
        "periodDays": days,
        "count": len(movies),
        "movies": movies
    }


# GET ALL MOVIES

@router.get("/")
def get_movies(
    page: int = Query(
        1,
        ge=1
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100
    )
):

    skip = (
        page - 1
    ) * limit

    movies = list(
        movies_collection.find(
            {},
            {
                "_id": 0
            }
        )
        .skip(skip)
        .limit(limit)
    )

    total = movies_collection.count_documents(
        {}
    )

    return {
        "success": True,
        "page": page,
        "limit": limit,
        "total": total,
        "movies": movies
    }


# SEARCH MOVIES

@router.get("/search/query")
def search_movies(
    q: str = Query(
        ...,
        min_length=1
    ),
    limit: int = Query(
        20,
        ge=1,
        le=50
    )
):

    search_query = q.strip()

    if not search_query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    movies = list(
        movies_collection.find(
            {
                "title": {
                    "$regex": search_query,
                    "$options": "i"
                }
            },
            {
                "_id": 0
            }
        )
        .limit(limit)
    )

    # Add TMDB metadata

    enriched_movies = []

    for movie in movies:
        enriched_movie = (
            enrich_movie_with_tmdb(
                movie
            )
        )

        enriched_movies.append(
            enriched_movie
        )

    return {
        "success": True,
        "query": search_query,
        "count": len(enriched_movies),
        "movies": enriched_movies
    }


# GET MOVIE BY ID

@router.get("/{movie_id}")
def get_movie(
    movie_id: int
):

    movie = movies_collection.find_one(
        {
            "movieId": movie_id
        },
        {
            "_id": 0
        }
    )

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    # Add TMDB metadata

    movie = enrich_movie_with_tmdb(
        movie
    )

    return {
        "success": True,
        "movie": movie
    }