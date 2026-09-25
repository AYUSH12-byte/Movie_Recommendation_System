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
    get_personalized_recommendations,
    get_cold_start_recommendations
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

    recommendations = (
        get_movie_recommendations(
            movie_title=movie_title,
            limit=limit
        )
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

    result = (
        get_personalized_recommendations(
            user_id=user_id,
            ratings=ratings,
            limit=limit
        )
    )

    return result


# COLD-START RECOMMENDATIONS

@router.get("/cold-start")
def cold_start_recommendations(
    limit: int = Query(
        10,
        ge=1,
        le=50
    )
):

    return get_cold_start_recommendations(
        limit=limit
    )


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

    # Get recommendation list

    result = (
        get_personalized_recommendations(
            user_id=user_id,
            ratings=ratings,
            limit=50
        )
    )

    recommendations = (
        result.get(
            "recommendations",
            []
        )
    )

    recommendation = None

    for item in recommendations:

        if int(
            item["movieId"]
        ) == movie_id:

            recommendation = item

            break

    # If not found in personalized list,
    # check cold-start recommendations.

    if not recommendation:

        cold_start_result = (
            get_cold_start_recommendations(
                limit=50
            )
        )

        cold_start_recommendations = (
            cold_start_result.get(
                "recommendations",
                []
            )
        )

        for item in cold_start_recommendations:

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
                "in the recommendation list."
            )
        )

    # Hybrid explanation

    if (
        result.get(
            "recommendationType"
        )
        == "hybrid"
        and
        recommendation.get(
            "sourceMovieTitle"
        )
    ):

        explanation = (

            f"This movie was recommended "
            f"because you rated "
            f"{recommendation['sourceMovieTitle']} "
            f"{recommendation.get('sourceUserRating')}/5. "

            f"It has a content similarity score "
            f"of {recommendation.get('similarity_score', 0)} "
            f"and a popularity score of "
            f"{recommendation.get('popularity_score', 0)}."
        )

        recommendation_type = "hybrid"

    # Cold-start explanation

    else:

        explanation = (

            "This movie was recommended as a "
            "popular choice for users without "
            "enough rating history for personalized "
            "recommendations. Its recommendation "
            "score is based on its average rating "
            "and the number of audience ratings."
        )

        recommendation_type = "cold_start"

    return {

        "success": True,

        "recommendationType": (
            recommendation_type
        ),

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

            "reason": explanation,

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

            "popularityScore": recommendation.get(
                "popularity_score"
            ),

            "recommendationScore": recommendation.get(
                "recommendation_score"
            ),

            "coldStartScore": recommendation.get(
                "coldStartScore"
            )
        }
    }