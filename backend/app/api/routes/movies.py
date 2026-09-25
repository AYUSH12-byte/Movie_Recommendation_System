from fastapi import (
    APIRouter,
    HTTPException,
    Query
)

from app.database.database import (
    movies_collection
)


router = APIRouter(
    prefix="/api/movies",
    tags=["Movies"]
)

# GET ALL MOVIES

@router.get("/")
def get_movies(
    page: int = 1,
    limit: int = 20
):

    if page < 1:
        page = 1

    if limit < 1:
        limit = 20

    if limit > 100:
        limit = 100

    skip = (page - 1) * limit

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

    total = movies_collection.count_documents({})

    return {
        "success": True,
        "page": page,
        "limit": limit,
        "total": total,
        "movies": movies
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

    return {
        "success": True,
        "movie": movie
    }

# Search

@router.get("/search/query")
def search_movies(
    q: str = Query(
        ...,
        min_length=1
    ),
    limit: int = 20
):

    movies = list(
        movies_collection.find(
            {
                "title": {
                    "$regex": q,
                    "$options": "i"
                }
            },
            {
                "_id": 0
            }
        )
        .limit(limit)
    )

    return {
        "success": True,
        "query": q,
        "count": len(movies),
        "movies": movies
    }