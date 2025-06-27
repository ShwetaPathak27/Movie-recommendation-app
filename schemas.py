from pydantic import BaseModel, field_validator
from datetime import timedelta
from typing import Optional

# 🔧 Base logic shared by both datasets
class BaseMovieSchema(BaseModel):
    title: str
    year: int
    rating: Optional[float]
    duration: Optional[str] = None
    genres: str
    director: str
    stars: str
    description: str

    @field_validator("duration", mode="before")
    @classmethod
    def convert_timedelta_to_str(cls, value):
        if value is None:
            return None
        if isinstance(value, timedelta):
            total_minutes = int(value.total_seconds() // 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m"
        if isinstance(value, str):
            return value.strip()
        raise ValueError("Duration must be a timedelta or a string")


# 🎬 IMDb Schema
class IMDbMovieCreate(BaseMovieSchema):
    pass

class IMDbMovieOut(IMDbMovieCreate):  # 🔄 FIXED: was IMDbMovie before
    id: int

    class Config:
        from_attributes = True


# 🎬 Kaggle Schema
class KaggleMovieCreate(BaseMovieSchema):
    pass

class KaggleMovieOut(KaggleMovieCreate):
    id: int

    class Config:
        from_attributes = True
