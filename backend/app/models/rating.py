from datetime import datetime

from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    movieId: int
    rating: float = Field(
        ...,
        ge=0.5,
        le=5.0
    )


class RatingResponse(BaseModel):
    id: str
    userId: str
    movieId: int
    rating: float
    createdAt: datetime