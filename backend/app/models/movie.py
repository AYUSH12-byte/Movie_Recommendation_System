from pydantic import BaseModel, Field


class MovieCreate(BaseModel):
    movieId: int
    title: str
    genres: str = ""


class MovieResponse(BaseModel):
    movieId: int
    title: str
    genres: str
    averageRating: float = 0.0
    totalRatings: int = 0