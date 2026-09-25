from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from app.api.dependencies import (
    get_current_user
)

from app.database.database import (
    ratings_collection
)

from app.services.recommendation_service import (
    get_movie_recommendations,
    get_personalized_recommendations
)


router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"]
)


# CONTENT-BASED RECOMMENDATIONS

@router.get("/movie/{movie_title}")
def movie_recommendations(
    movie_title: str,
    limit: int = Query(
        10,
        ge=1,
        le=50
    )
):

    recommendations = get_movie_recommendations(
        movie_title=movie_title,
        limit=limit
    )

    if not recommendations:

        raise HTTPException(
            status_code=404,
            detail=(
                "Movie not found or no "
                "recommendations available"
            )
        )

    return {
        "success": True,
        "type": "content_based",
        "movie": movie_title,
        "count": len(recommendations),
        "recommendations": recommendations
    }


# PERSONALIZED RECOMMENDATIONS

@router.get("/personalized")
def personalized_recommendations(
    limit: int = Query(
        10,
        ge=1,
        le=50
    ),
    current_user=Depends(
        get_current_user
    )
):

    user_id = str(
        current_user["_id"]
    )

    # Get user's ratings

    ratings = list(
        ratings_collection.find(
            {
                "userId": user_id
            },
            {
                "_id": 0,
                "userId": 1,
                "movieId": 1,
                "rating": 1
            }
        )
    )

    # Generate recommendations

    result = get_personalized_recommendations(
        user_id=user_id,
        ratings=ratings,
        limit=limit
    )

    return result


# RECOMMENDATION EXPLANATION

@router.get(
    "/personalized/{movie_id}/explanation"
)
def recommendation_explanation(
    movie_id: int,
    current_user=Depends(
        get_current_user
    )
):

    user_id = str(
        current_user["_id"]
    )

    # Get user's ratings

    ratings = list(
        ratings_collection.find(
            {
                "userId": user_id
            },
            {
                "_id": 0,
                "userId": 1,
                "movieId": 1,
                "rating": 1
            }
        )
    )

    if not ratings:

        raise HTTPException(
            status_code=400,
            detail=(
                "Rate some movies first to "
                "generate recommendation explanations."
            )
        )

    # Generate personalized recommendations

    result = get_personalized_recommendations(
        user_id=user_id,
        ratings=ratings,
        limit=50
    )

    recommendations = (
        result.get(
            "recommendations",
            []
        )
    )

    # Find requested recommendation

    recommendation = None

    for item in recommendations:

        if int(
            item["movieId"]
        ) == movie_id:

            recommendation = item
            break

    if not recommendation:

        raise HTTPException(
            status_code=404,
            detail=(
                "This movie is not currently "
                "in your personalized recommendations."
            )
        )

    # Return explanation

    return {
        "success": True,
        "movie": {
            "movieId": recommendation[
                "movieId"
            ],
            "title": recommendation[
                "title"
            ],
            "genres": recommendation[
                "genres"
            ]
        },
        "explanation": {
            "reason": recommendation.get(
                "reason",
                "Recommended based on your "
                "movie preferences."
            ),
            "sourceMovieId": recommendation.get(
                "sourceMovieId"
            ),
            "sourceMovieTitle": recommendation.get(
                "sourceMovieTitle"
            ),
            "yourRating": recommendation.get(
                "sourceUserRating"
            ),
            "similarityScore": recommendation.get(
                "similarity_score"
            ),
            "recommendationScore": recommendation.get(
                "recommendation_score"
            )
        }
    }