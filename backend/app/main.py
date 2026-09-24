from fastapi import FastAPI

app = FastAPI(
    title="Movie Recommendation System API",
    description="AI-powered movie recommendation system",
    version="1.0.0"
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