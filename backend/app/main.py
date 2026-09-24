from fastapi import FastAPI

from app.api.routes.recommendations import (
    router as recommendation_router
)


app = FastAPI(
    title="Movie Recommendation System API",
    description="AI-powered movie recommendation system",
    version="1.0.0"
)


# ==========================================
# ROUTES
# ==========================================

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

    return {
        "status": "success",
        "message": "Backend is healthy"
    }