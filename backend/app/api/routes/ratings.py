from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.models.rating import (
    RatingCreate
)

from app.api.dependencies import (
    get_current_user
)

from app.services.rating_service import (
    create_or_update_rating,
    get_user_ratings,
    get_user_movie_rating,
    delete_rating
)


router = APIRouter(
    prefix="/api/ratings",
    tags=["Ratings"]
)


# ADD / UPDATE RATING

@router.post("/")
def rate_movie(
    rating_data: RatingCreate,
    current_user=Depends(
        get_current_user
    )
):

    result = create_or_update_rating(
        user_id=str(
            current_user["_id"]
        ),
        movie_id=rating_data.movieId,
        rating=rating_data.rating
    )

    if not result["success"]:

        raise HTTPException(
            status_code=404,
            detail=result["message"]
        )

    return result


# GET MY RATINGS

@router.get("/my")
def my_ratings(
    current_user=Depends(
        get_current_user
    )
):

    ratings = get_user_ratings(
        str(current_user["_id"])
    )

    return {
        "success": True,
        "count": len(ratings),
        "ratings": ratings
    }


# GET MY RATING FOR MOVIE

@router.get("/movie/{movie_id}")
def my_movie_rating(
    movie_id: int,
    current_user=Depends(
        get_current_user
    )
):

    rating = get_user_movie_rating(
        user_id=str(
            current_user["_id"]
        ),
        movie_id=movie_id
    )

    return {
        "success": True,
        "rating": rating
    }


# DELETE MY RATING

@router.delete("/movie/{movie_id}")
def remove_rating(
    movie_id: int,
    current_user=Depends(
        get_current_user
    )
):

    result = delete_rating(
        user_id=str(
            current_user["_id"]
        ),
        movie_id=movie_id
    )

    if not result["success"]:

        raise HTTPException(
            status_code=404,
            detail=result["message"]
        )

    return result