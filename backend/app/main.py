from fastapi import FastAPI

from app.api.routes.auth import (
    router as auth_router
)

from app.api.routes.movies import (
    router as movie_router
)

from app.api.routes.recommendations import (
    router as recommendation_router
)

from app.database.database import (
    check_database_connection
)

from app.database.indexes import (
    create_indexes
)


app = FastAPI(
    title="Movie Recommendation System API",
    description="AI-powered movie recommendation system",
    version="1.0.0"
)


create_indexes()


app.include_router(
    auth_router
)

app.include_router(
    movie_router
)

app.include_router(
    recommendation_router
)


@app.get("/")
def root():

    return {
        "message": "Movie Recommendation System API is running"
    }


@app.get("/api/health")
def health_check():

    database_status = check_database_connection()

    return {
        "status": "success",
        "backend": "healthy",
        "database": database_status
    }