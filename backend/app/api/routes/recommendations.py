from fastapi import APIRouter, HTTPException

from app.services.recommendation_service import (
    get_movie_recommendations
)


router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"]
)


@router.get("/movie/{movie_title}")
def recommend_movies(
    movie_title: str,
    limit: int = 10
):

    recommendations = get_movie_recommendations(
        movie_title,
        limit
    )

    if not recommendations:

        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    return {
        "success": True,
        "movie": movie_title,
        "count": len(recommendations),
        "recommendations": recommendations
    }